"""Stage 0: merge the per-topic TransGull API dumps into data/00_segments.jsonl.

Usage: python3 -I pipeline/stage0_unify.py <project_root>
Reads raw/refetch_20261108/topic_<id>_messages.json (messages/list responses). `completed_at` is when a line
was recognised live; `updated_at` moves when an operator edits the text later, so it only feeds the `edited` flag.
"""
import csv
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

TOPICS = {  # topic_id -> (day, stage)
    290151883: ("2026-11-05", "main"),
    738651866: ("2026-11-05", "main"),
    1901713953: ("2026-11-05", "breakout"),
    1842167111: ("2026-11-06", "main"),
}
RAW_DIR = "raw/refetch_20261108"
CJK = re.compile(r"[一-鿿]")
LATIN = re.compile(r"[A-Za-z]")


def guess_lang(text):
    cjk, latin = len(CJK.findall(text)), len(LATIN.findall(text))
    if cjk == 0 and latin == 0:
        return "unk"
    return "zh" if cjk * 3 >= latin else "en"  # one CJK char carries roughly a word


def to_local(ts):
    return (datetime.fromisoformat(ts.replace("Z", "+00:00")) + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")


def main(root):
    root = Path(root)
    out, report = [], []
    for topic_id, (day, stage) in TOPICS.items():
        path = root / f"{RAW_DIR}/topic_{topic_id}_messages.json"
        rows = json.loads(path.read_text(encoding="utf-8"))["data"]["items"]
        rows.sort(key=lambda r: r["message_order"])
        orders = [r["message_order"] for r in rows]
        dupes = len(orders) - len(set(orders))
        gaps = sum(1 for a, b in zip(orders, orders[1:]) if b - a > 1)
        for r in rows:
            text = r["source_text"] or ""
            tr = {t["target_language"]: t.get("translated_text") or "" for t in r.get("translations") or []}
            out.append({
                "seg_id": f"{topic_id}:{r['message_order']}",
                "topic_id": topic_id,
                "order": r["message_order"],
                "day": day,
                "stage": stage,
                "ts_local": to_local(r["completed_at"]),
                "edited": r["updated_at"][:16] != r["completed_at"][:16],
                "lang": r.get("source_language") or guess_lang(text),
                "lang_guessed": not r.get("source_language"),
                "source_text": text,
                "zh": tr.get("zh", ""),
                "en": tr.get("en", ""),
            })
        report.append(f"{topic_id} {day} {stage}: {len(rows)} segs, order {orders[0]}..{orders[-1]}, dupes={dupes}, gaps={gaps}")
    dest = root / "data/00_segments.jsonl"
    with dest.open("w", encoding="utf-8") as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("\n".join(report))
    print(f"total {len(out)} -> {dest}")

    with (root / "data/agenda.csv").open(encoding="utf-8") as f:
        agenda = list(csv.DictReader(f))
    print(f"agenda: {len(agenda)} sessions; per topic:",
          {t: sum(1 for a in agenda if int(a['topic_id']) == t) for t in TOPICS})


if __name__ == "__main__":
    main(sys.argv[1])
