"""Stage 1 merge: combine per-window LLM segmentation, cross-check with Jev, build talk table + review page.

Usage: python3 -I pipeline/stage1_merge.py <project_root>
Reads   data/seg_llm/w*/llm_labels.json (+ the validated eval window), data/seg_jev/<topic>/jev_raw.jsonl
Writes  data/01_segment_labels.jsonl, data/01_talks.csv, out/boundaries_review.html
"""
import csv
import html
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

# The validated eval window is reused for 738651866:1185-1859 (w03 re-does 1860+ so TiDB stays in one window)
EXTRA_WINDOWS = [("eval_1h", 738651866, "data/eval_1h/llm_labels.json", 1185, 1859)]
JEV_NOT_TALK = 0.2   # LLM says talk but Jev's p(talk) is below this
JEV_TALK = 0.8       # LLM says non-talk but Jev's p(talk) is above this
EDGE = 4             # lines shown on each side of a boundary in the review page
EVENT_HOURS = ("08:00", "19:00")  # timestamps outside this were edited after the event
GAP_MIN = 3          # minutes without any transcript line inside a talk
LONG_LINE = 300      # chars; a line this long can legitimately cover several minutes


def robust_time(segs):
    """HH:MM from the median timestamp of a few segments. Lines edited after the event carry evening
    timestamps, so anything outside the event's daytime hours is ignored."""
    ts = sorted(x["ts_local"] for x in segs if EVENT_HOURS[0] <= x["ts_local"][11:16] <= EVENT_HOURS[1])
    return ts[len(ts) // 2][11:16] if ts else ""


def minutes(hhmm_ss):
    h, m, sec = (int(x) for x in hhmm_ss.split(":"))
    return h * 60 + m + sec / 60


def coverage_note(segs, agenda_row):
    """Flag talks whose transcript looks incomplete: long silent gaps, or far shorter than the slot."""
    timed = [(minutes(x["ts_local"][11:19]), len(x["source_text"])) for x in segs]
    ts = [t for t, _ in timed]
    notes = []
    # a long silence between two short lines means missing audio; next to a very long line it is a merged segment
    gaps = [(b - a) for (a, n1), (b, n2) in zip(timed, timed[1:]) if b - a >= GAP_MIN and max(n1, n2) < LONG_LINE]
    if gaps:
        notes.append(f"{len(gaps)} 处转录空档 ≥{GAP_MIN} 分钟（最长 {max(gaps):.0f} 分钟）")
    if agenda_row.get("sched_start") and ts:
        slot = minutes(agenda_row["sched_end"] + ":00") - minutes(agenda_row["sched_start"] + ":00")
        spoken = sorted(ts)[-1] - sorted(ts)[0]
        if spoken < 0.5 * slot:
            notes.append(f"转录只覆盖 {spoken:.0f} 分钟（议程时长 {slot:.0f} 分钟）")
    return "；".join(notes)


def load_windows(root):
    out = []
    for f in sorted((root / "data/seg_llm").glob("w*/llm_labels.json")):
        wdir = f.parent
        first = wdir.joinpath("window.txt").open(encoding="utf-8").readline()
        prompt = wdir.joinpath("prompt.md").read_text(encoding="utf-8")
        topic = int(prompt.split("This window (")[1].split(":")[0])
        out.append((wdir.name, topic, json.loads(f.read_text(encoding="utf-8")), int(first.split("\t")[0]), None))
    for wid, topic, path, lo, hi in EXTRA_WINDOWS:
        out.append((wid, topic, json.loads((root / path).read_text(encoding="utf-8")), lo, hi))
    return out


def main(root):
    root = Path(root)
    segs = [json.loads(line) for line in (root / "data/00_segments.jsonl").open(encoding="utf-8")]
    by_id = {s["seg_id"]: s for s in segs}
    agenda = {a["session_id"]: a for a in csv.DictReader((root / "data/agenda.csv").open(encoding="utf-8"))}
    jev = {}
    for f in (root / "data/seg_jev").glob("*/jev_raw.jsonl"):
        for line in f.open(encoding="utf-8"):
            r = json.loads(line)
            jev[r["seg_id"]] = r

    label, window_of, notes = {}, {}, []
    for wid, topic, doc, lo, hi in load_windows(root):
        notes.append((wid, doc.get("notes", ""), doc.get("sessions_found", [])))
        for sp in doc["spans"]:
            for o in range(sp["from"], sp["to"] + 1):
                if hi is not None and not lo <= o <= hi:
                    continue
                sid = f"{topic}:{o}"
                if sid in by_id:
                    assert sid not in label, f"{sid} labelled twice ({window_of[sid]}, {wid})"
                    label[sid] = (sp["type"], sp.get("session_id") if sp["type"] == "talk" else None)
                    window_of[sid] = wid
    missing = [s["seg_id"] for s in segs if s["seg_id"] not in label]

    # per-segment table with the Jev cross-check
    rows = []
    for s in segs:
        t, sess = label.get(s["seg_id"], ("unlabelled", None))
        j = jev.get(s["seg_id"])
        p_talk = j["probs"].get("talk", 0) if j else None
        flag = None
        if p_talk is not None and t == "talk" and p_talk < JEV_NOT_TALK:
            flag = "jev_says_not_talk"
        elif p_talk is not None and t in ("host", "logistics", "noise") and p_talk > JEV_TALK:
            flag = "jev_says_talk"
        rows.append({"seg_id": s["seg_id"], "topic_id": s["topic_id"], "order": s["order"], "type": t,
                     "session_id": sess, "window": window_of.get(s["seg_id"]),
                     "jev_type": j["pred_type"] if j else None,
                     "jev_p_talk": round(p_talk, 3) if p_talk is not None else None, "flag": flag})
    with (root / "data/01_segment_labels.jsonl").open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # talk table
    per_topic = defaultdict(list)
    for r in rows:
        per_topic[r["topic_id"]].append(r)
    talks = {}
    for topic, rs in per_topic.items():
        rs.sort(key=lambda r: r["order"])
        for i, r in enumerate(rs):
            if r["type"] == "talk" and r["session_id"]:
                t = talks.setdefault(r["session_id"], {"topic_id": topic, "idx": [], "all": rs})
                assert t["topic_id"] == topic, f"{r['session_id']} spans topics"
                t["idx"].append(i)
    talk_rows = []
    for sess, t in talks.items():
        rs, idx = t["all"], t["idx"]
        first, last = rs[idx[0]], rs[idx[-1]]
        inside = rs[idx[0]:idx[-1] + 1]
        stripped_inside = sum(1 for r in inside if r["type"] != "talk")
        other_sessions = Counter(r["session_id"] for r in inside if r["type"] == "talk" and r["session_id"] != sess)
        texts = [by_id[rs[i]["seg_id"]] for i in idx]
        langs = Counter(x["lang"] for x in texts)
        a = agenda.get(sess, {})
        talk_rows.append({
            "talk_id": sess, "on_agenda": sess in agenda, "day": a.get("day", by_id[first["seg_id"]]["day"]),
            "stage": a.get("stage", by_id[first["seg_id"]]["stage"]), "format": a.get("format", "offagenda"),
            "speakers": a.get("speakers", sess.split(":", 1)[-1]), "orgs": a.get("orgs", ""), "title": a.get("title", ""),
            "topic_id": t["topic_id"], "seg_start": first["order"], "seg_end": last["order"],
            "n_talk_segs": len(idx), "n_stripped_inside": stripped_inside,
            "interleaved_with": ";".join(other_sessions) if other_sessions else "",
            "main_lang": langs.most_common(1)[0][0], "chars": sum(len(x["source_text"]) for x in texts),
            "sched_start": a.get("sched_start", ""), "actual_start": robust_time(texts[:15]),
            "actual_end": robust_time(texts[-5:]),
            "jev_flags": sum(1 for r in inside if r["flag"]),
            "coverage_note": coverage_note(texts, a),
        })
    talk_rows.sort(key=lambda r: (r["day"], r["stage"] != "main", r["topic_id"], r["seg_start"]))
    with (root / "data/01_talks.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(talk_rows[0].keys()))
        w.writeheader()
        w.writerows(talk_rows)

    not_found = [s for s in agenda if s not in talks]
    render(root, rows, by_id, talk_rows, talks, not_found, missing, notes)
    types = Counter(r["type"] for r in rows)
    flags = Counter(r["flag"] for r in rows if r["flag"])
    print(f"segments {len(rows)} labelled {len(rows) - len(missing)} types {dict(types)}")
    print(f"talks {len(talk_rows)} (agenda {sum(r['on_agenda'] for r in talk_rows)}, offagenda {sum(not r['on_agenda'] for r in talk_rows)}); agenda not found: {not_found}")
    print(f"jev flags {dict(flags)}; interleaved: {[r['talk_id'] for r in talk_rows if r['interleaved_with']]}")


def render(root, rows, by_id, talk_rows, talks, not_found, missing, notes):
    esc = html.escape

    def line(r, cls=""):
        s = by_id[r["seg_id"]]
        flag = f' <span class="flag">{"Jev:非正文" if r["flag"] == "jev_says_not_talk" else "Jev:正文"} {r["jev_p_talk"]}</span>' if r["flag"] else ""
        return (f'<div class="ln {r["type"]} {cls}"><span class="o">{r["order"]}</span><span class="tp">{r["type"]}</span>'
                f'<span class="tm">{s["ts_local"][11:19]}</span>{esc(s["source_text"][:160])}{flag}</div>')

    cards = []
    for tr in talk_rows:
        t = talks[tr["talk_id"]]
        rs, idx = t["all"], t["idx"]
        a, b = idx[0], idx[-1]
        head = [line(r) for r in rs[max(0, a - EDGE):a]] + [line(r, "in") for r in rs[a:min(a + EDGE, b + 1)]]
        tail = [line(r, "in") for r in rs[max(b - EDGE + 1, a):b + 1]] + [line(r) for r in rs[b + 1:b + 1 + EDGE]]
        inside_flags = [line(r, "in") for r in rs[a:b + 1] if r["flag"] or r["type"] != "talk"]
        warn = []
        if not tr["on_agenda"]:
            warn.append("议程外")
        if tr["interleaved_with"]:
            warn.append(f"区间内夹着其他场次: {tr['interleaved_with']}")
        if tr["n_stripped_inside"]:
            warn.append(f"区间内剥离 {tr['n_stripped_inside']} 段")
        if tr["jev_flags"]:
            warn.append(f"Jev 不一致 {tr['jev_flags']} 段")
        if tr["coverage_note"]:
            warn.append(tr["coverage_note"])
        cards.append(f"""<section class="card" id="{esc(tr['talk_id'])}">
<h3>{esc(tr['talk_id'])} · {esc(tr['speakers'])} <small>{esc(tr['orgs'])}</small></h3>
<div class="meta">{esc(tr['title'])}<br>{tr['day']} {tr['stage']} · 议程 {tr['sched_start'] or '—'} · 实际 {tr['actual_start']}–{tr['actual_end']} ·
seg {tr['topic_id']}:{tr['seg_start']}–{tr['seg_end']} · {tr['n_talk_segs']} 段 / {tr['chars']:,} 字符 · {tr['main_lang']}
{''.join(f'<span class="warn">{esc(w)}</span>' for w in warn)}</div>
<div class="cols"><div><h4>开头</h4>{''.join(head)}</div><div><h4>结尾</h4>{''.join(tail)}</div></div>
{f'<details><summary>区间内被剥离或 Jev 不一致的段（{len(inside_flags)}）</summary>{"".join(inside_flags)}</details>' if inside_flags else ''}
</section>""")

    outside_flags = [r for r in rows if r["flag"] == "jev_says_talk"]
    toc = "".join(f'<a href="#{esc(t["talk_id"])}" class="{"warnlink" if (t["jev_flags"] or t["interleaved_with"] or not t["on_agenda"] or t["coverage_note"]) else ""}">{esc(t["talk_id"])}</a>' for t in talk_rows)
    note_html = "".join(f"<li><b>{esc(w)}</b>：{esc(n)}</li>" for w, n, _ in notes if n)
    page = f"""<!doctype html><html lang="zh"><meta charset="utf-8"><title>切分复核 · AIE Shanghai 2026</title>
<style>
body{{font:14px/1.5 -apple-system,"PingFang SC",sans-serif;margin:24px auto;max-width:1300px;color:#222;padding:0 16px}}
.card{{border:1px solid #e3e3e3;border-radius:10px;padding:12px 16px;margin:16px 0}} h3{{margin:0 0 4px}} h3 small{{color:#666;font-weight:normal}}
.meta{{color:#555;font-size:12px;margin-bottom:8px}} .warn{{background:#fff1d6;color:#8a5300;border-radius:4px;padding:0 6px;margin-left:6px}}
.cols{{display:grid;grid-template-columns:1fr 1fr;gap:16px}} h4{{margin:4px 0;font-size:12px;color:#888}}
.ln{{font-size:12.5px;padding:1px 4px;border-left:3px solid #ccc;margin:1px 0}} .ln.in{{background:#f4f6ff}}
.ln.talk{{border-color:#4a6cf7}} .ln.host{{border-color:#f2994a;color:#8a5a2b}} .ln.logistics{{border-color:#9aa0a6;color:#777}} .ln.noise{{border-color:#d93025;color:#999}}
.o{{display:inline-block;width:44px;color:#999}} .tp{{display:inline-block;width:64px;color:#999;font-size:11px}} .tm{{display:inline-block;width:64px;color:#bbb;font-size:11px}}
.flag{{background:#fde7e9;color:#b3261e;border-radius:4px;padding:0 4px;font-size:11px;margin-left:6px}}
.toc a{{display:inline-block;margin:2px 6px 2px 0;font-size:12px}} .toc a.warnlink{{color:#b26a00;font-weight:600}}
.kpi{{display:flex;gap:16px;flex-wrap:wrap}} .kpi div{{background:#f5f5f7;padding:8px 12px;border-radius:8px}} .kpi b{{display:block;font-size:18px}}
</style>
<h1>切分复核 · AIE Shanghai 2026</h1>
<p><b>这页给谁看</b>：复核演讲切分是否干净。每场演讲列出开头和结尾各 {EDGE} 段：浅蓝底是保留的正文，前后无底色的是被剥掉的串场/场务。
红色标签是 Jev 与 LLM 判断不一致的段，优先看。橙色链接的场次有需要注意的地方。</p>
<div class="kpi">
<div>识别到的演讲<b>{len(talk_rows)}</b></div><div>议程外<b>{sum(not t['on_agenda'] for t in talk_rows)}</b></div>
<div>议程中未找到<b>{len(not_found)}</b></div><div>未标注段<b>{len(missing)}</b></div>
<div>Jev 不一致：正文被判非正文<b>{sum(r['flag'] == 'jev_says_not_talk' for r in rows)}</b></div>
<div>Jev 不一致：剥离段被判正文<b>{len(outside_flags)}</b></div>
</div>
{f'<p class="warn">议程中未找到：{esc(", ".join(not_found))}</p>' if not_found else ''}
<div class="toc">{toc}</div>
<details><summary>各窗口子 agent 的备注</summary><ul>{note_html}</ul></details>
{''.join(cards)}
<h2>被剥离、但 Jev 认为是正文的段（{len(outside_flags)}）</h2>
{''.join(line(r) for r in outside_flags)}
</html>"""
    (root / "out/boundaries_review.html").write_text(page, encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1])
