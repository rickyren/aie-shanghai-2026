"""Label every segment in a range with Jev, then cut it into talk sessions with simple rules.

Usage: .venv/bin/python -I pipeline/jev_segment.py <project_root> <topic_id> <from> <to> <out_dir> <session_id,...> [--reuse]
--reuse re-cuts from the cached jev_raw.jsonl without calling the API.
Writes <out_dir>/jev_raw.jsonl (per-segment answers) and <out_dir>/jev_labels.json (spans).
"""
import asyncio
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from jev_common import api_key, classify  # noqa: E402

ISOLATED_MAX = 2      # runs this short can be flipped by their neighbours
FLANK_MIN = 3         # ...if both neighbouring runs are at least this long
HOST_SPLIT_P = 0.6    # a confident host segment inside a gap separates two sessions
LONG_GAP = 8          # so does any non-talk gap at least this long
INTRO_WINDOW = 6      # the host intro must sit right before the block it introduces


def runs(labels):
    """[(label, start_idx, end_idx_inclusive)] over a list of labels."""
    out, i = [], 0
    while i < len(labels):
        j = i
        while j + 1 < len(labels) and (labels[j + 1] == "talk") == (labels[i] == "talk"):
            j += 1
        out.append(("talk" if labels[i] == "talk" else "other", i, j))
        i = j + 1
    return out


def segment(rows, sessions):
    labels = [r["pred_type"] for r in rows]
    p_host = [r["probs"].get("host", 0) for r in rows]
    start_p = [r["start_p"] for r in rows]

    # 0. `noise` is rare and tends to swallow odd talk lines (e.g. a speaker reading a demo prompt):
    #    resolve each noise run to its neighbours' label, preferring talk when either side is talk
    i = 0
    while i < len(labels):
        if labels[i] != "noise":
            i += 1
            continue
        j = i
        while j + 1 < len(labels) and labels[j + 1] == "noise":
            j += 1
        left = labels[i - 1] if i > 0 else None
        right = labels[j + 1] if j + 1 < len(labels) else None
        fill = "talk" if "talk" in (left, right) else (left or right or "logistics")
        for k in range(i, j + 1):
            labels[k] = fill
        i = j + 1

    # 1. isolated non-talk inside a talk, without a confident host signal -> talk
    rs = runs(labels)
    for k in range(1, len(rs) - 1):
        kind, a, b = rs[k]
        if kind == "other" and b - a + 1 <= ISOLATED_MAX \
                and rs[k - 1][2] - rs[k - 1][1] + 1 >= FLANK_MIN and rs[k + 1][2] - rs[k + 1][1] + 1 >= FLANK_MIN \
                and max(p_host[a:b + 1]) < HOST_SPLIT_P:
            for i in range(a, b + 1):
                labels[i] = "talk"
    # 2. isolated talk inside a non-talk stretch, with no talk_start signal -> take the neighbours' type
    rs = runs(labels)
    for k in range(1, len(rs) - 1):
        kind, a, b = rs[k]
        if kind == "talk" and b - a + 1 <= ISOLATED_MAX \
                and rs[k - 1][2] - rs[k - 1][1] + 1 >= FLANK_MIN and rs[k + 1][2] - rs[k + 1][1] + 1 >= FLANK_MIN \
                and max(r["start_p"] for r in rows[a:b + 1]) < 0.5:
            for i in range(a, b + 1):
                labels[i] = labels[a - 1]

    # 3. talk blocks -> sessions. A gap with a confident host segment always splits.
    #    Without one, a short gap just continues the previous session; after a long host-less gap
    #    (break / stage setup) a block only counts as a new session if it opens with a talk_start signal,
    #    otherwise it is setup chatter and becomes logistics.
    blocks = []
    for kind, a, b in runs(labels):
        if kind != "talk":
            continue
        gap = range(blocks[-1][1] + 1 if blocks else 0, a)
        host_intro = any(labels[i] == "host" and p_host[i] >= HOST_SPLIT_P for i in gap[-INTRO_WINDOW:])
        opens = max(start_p[a:min(b + 1, a + 5)]) >= 0.5
        if blocks and not host_intro and len(gap) < LONG_GAP:
            blocks[-1][1] = b
        elif blocks and not host_intro and not opens:
            for i in range(a, b + 1):
                labels[i] = "logistics"
        elif not blocks and a > 0 and not host_intro and not opens:
            for i in range(a, b + 1):
                labels[i] = "logistics"
        else:
            blocks.append([a, b])

    # 4. assign blocks to the window's agenda sessions in order
    session_of = {}
    for n, (a, b) in enumerate(blocks):
        sid = sessions[n] if n < len(sessions) else f"extra{n - len(sessions) + 1}"
        for i in range(a, b + 1):
            if labels[i] == "talk":
                session_of[i] = sid
    spans = []
    for i, r in enumerate(rows):
        key = (labels[i], session_of.get(i))
        if spans and (spans[-1]["type"], spans[-1].get("session_id")) == key:
            spans[-1]["to"] = r["order"]
        else:
            spans.append({"from": r["order"], "to": r["order"], "type": labels[i],
                          **({"session_id": key[1]} if key[1] else {})})
    return spans, len(blocks)


def main(root, topic, lo, hi, out_dir, sessions, reuse=False):
    root, out_dir = Path(root), Path(out_dir)
    segs = {}
    for line in (root / "data/00_segments.jsonl").open(encoding="utf-8"):
        r = json.loads(line)
        segs[r["seg_id"]] = r
    items = [{"seg_id": sid, "order": r["order"]} for sid, r in segs.items()
             if r["topic_id"] == int(topic) and int(lo) <= r["order"] <= int(hi)]
    raw = out_dir / "jev_raw.jsonl"
    if reuse and raw.exists():  # re-cut from cached answers, no API calls
        rows = [json.loads(line) for line in raw.open(encoding="utf-8")]
        prev = json.loads((out_dir / "jev_labels.json").read_text(encoding="utf-8"))["stats"]
        wall = prev["wall_s"]
    else:
        t0 = time.perf_counter()
        rows = asyncio.run(classify(items, segs, api_key()))
        wall = time.perf_counter() - t0
        errors = [r for r in rows if "error" in r]
        assert not errors, errors[0]["error"]
        rows.sort(key=lambda r: r["order"])
        with raw.open("w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps({k: v for k, v in r.items() if k != "state"}, ensure_ascii=False) + "\n")
    spans, n_blocks = segment(rows, sessions.split(","))
    tokens = sum(r["in_tok"] for r in rows)
    (out_dir / "jev_labels.json").write_text(json.dumps(
        {"method": "jev", "spans": spans, "stats": {"segments": len(rows), "wall_s": round(wall, 1),
                                                    "input_tokens": tokens, "blocks": n_blocks}},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(rows)} segs in {wall:.1f}s, {tokens:,} tokens, {n_blocks} talk blocks")
    for s in spans:
        print(s)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--reuse"]
    main(*args, reuse="--reuse" in sys.argv)
