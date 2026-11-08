"""Side-by-side review page for proofread talks: raw ASR lines vs. clean paragraphs.

Usage: python3 -I pipeline/review_clean.py <project_root> <out_html> [<file_id> ...]   (no ids = every finished talk)
"""
import csv
import html
import json
import re
import sys
from pathlib import Path

SEG = re.compile(r"\[seg\s*(\d+)(?:\s*[–-]\s*(\d+))?\]\s*$")  # [seg A–B] or single-line [seg N]


def parse_md(text):
    """-> front matter dict, [(kind, text, (a, b) | None)] where kind is 'h' or 'p'."""
    fm, body = {}, text
    if text.startswith("---"):
        _, head, body = text.split("---", 2)
        for line in head.strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip()
    blocks = []
    for chunk in re.split(r"\n\s*\n", body.strip()):
        chunk = chunk.strip()
        if not chunk:
            continue
        if chunk.startswith("#"):
            blocks.append(("h", chunk.lstrip("#").strip(), None))
            continue
        m = SEG.search(chunk)
        rng = (int(m.group(1)), int(m.group(2) or m.group(1))) if m else None
        text = SEG.sub("", chunk).strip()
        if not text and rng:
            # a "[seg A–B]" on its own line belongs to the paragraph(s) right above it
            for i in range(len(blocks) - 1, -1, -1):
                if blocks[i][0] != "p" or blocks[i][2] is not None:
                    break
                blocks[i] = ("p", blocks[i][1], rng)
            continue
        blocks.append(("p", text, rng))
    return fm, blocks


def md_inline(s):
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = s.replace("〔?〕", '<mark class="q">〔?〕</mark>')
    s = re.sub(r"〔(无法辨识|unintelligible)〕", r'<mark class="q">〔\1〕</mark>', s)
    return s.replace("\n", "<br>")


def talk_section(root, tid):
    raw = {}
    for line in (root / f"data/03_clean/_input/{tid}.txt").open(encoding="utf-8"):
        o, t = line.rstrip("\n").split("\t", 1)
        raw[int(o)] = t
    md = (root / f"data/03_clean/{tid}.md").read_text(encoding="utf-8")
    notes = json.loads((root / f"data/03_clean/{tid}.notes.json").read_text(encoding="utf-8"))
    fm, blocks = parse_md(md)
    paras = [b for b in blocks if b[0] == "p"]
    covered = set()
    for _, _, r in paras:
        if r:
            covered |= {o for o in raw if r[0] <= o <= r[1]}
    raw_chars = sum(len(t) for t in raw.values())
    clean_chars = sum(len(b[1]) for b in blocks)
    q = md.count("〔?〕") + len(re.findall(r"〔(无法辨识|unintelligible)〕", md))
    removed = set()
    for item in notes.get("removed_non_content", []):
        for a, b in re.findall(r"(\d+)\s*(?:[–-]\s*(\d+))?", str(item.get("orders", ""))):
            removed |= set(range(int(a), int(b or a) + 1))
    uncovered = sorted(set(raw) - covered - removed)

    rows = []
    for kind, text, r in blocks:
        if kind == "h":
            rows.append(f'<tr class="h"><td></td><td><h4>{html.escape(text)}</h4></td></tr>')
            continue
        left = "".join(f'<div class="raw"><span class="o">{o}</span>{html.escape(raw[o])}</div>'
                       for o in sorted(raw) if r and r[0] <= o <= r[1])
        rows.append(f'<tr><td class="l">{left or "<i>无范围</i>"}</td>'
                    f'<td class="r">{md_inline(text)}<div class="rng">{f"seg {r[0]}–{r[1]}" if r else "缺少 seg 标注"}</div></td></tr>')

    def table(items, cols):
        if not items:
            return "<p class=muted>无</p>"
        head = "".join(f"<th>{c}</th>" for c, _ in cols)
        body = "".join("<tr>" + "".join(f"<td>{html.escape(str(it.get(k, '')))}</td>" for _, k in cols) + "</tr>" for it in items)
        return f"<table class=mini><tr>{head}</tr>{body}</table>"

    ver = notes.get("verified", [])
    spk = "".join(
        f"<li><b>{html.escape(s.get('name', ''))}</b>（识别为：{html.escape('、'.join(s.get('name_as_heard', [])))}）· "
        f"{html.escape(s.get('org', ''))} · {html.escape(s.get('role', ''))}<br>"
        f"<span class=muted>{html.escape(s.get('background', ''))} · seg {html.escape(str(s.get('evidence_orders', '')))}</span></li>"
        for s in notes.get("speakers", []))
    stats = {"id": tid, "talk_id": fm.get("talk_id", tid), "speakers": fm.get("speakers", ""), "ratio": clean_chars / raw_chars,
             "paras": len(paras), "q": q, "uncovered": len(uncovered), "verified": sum(1 for v in ver if v.get("resolved_to")),
             "corrections": len(notes.get("corrections", [])), "topic_note": bool(notes.get("actual_topic_note"))}
    return stats, f"""<section id="{tid}">
<h2>{tid} · {html.escape(fm.get('speakers', ''))} <small>{html.escape(fm.get('orgs', ''))}</small></h2>
<p class=muted>{html.escape(fm.get('title', ''))} · {fm.get('language', '')}</p>
<div class="kpi"><div>清稿/原文字符比<b>{clean_chars / raw_chars:.0%}</b></div><div>段落<b>{len(paras)}</b></div>
<div>〔?〕存疑<b>{q}</b></div><div>未覆盖的原始行<b>{len(uncovered)}</b></div></div>
{f'<p class=warn>未被任何段落覆盖的行：{", ".join(map(str, uncovered[:40]))}{" …" if len(uncovered) > 40 else ""}</p>' if uncovered else ''}
{f'<p class=warn>与议程不同：{html.escape(notes["actual_topic_note"])}</p>' if notes.get("actual_topic_note") else ''}
<details open><summary>发言人信息（仅来自本场转录）</summary><ul>{spk}</ul></details>
<details open><summary>主要纠错（{len(notes.get('corrections', []))}）</summary>{table(notes.get('corrections', []), [('识别为', 'from'), ('改为', 'to'), ('次数', 'count'), ('把握', 'confidence')])}</details>
<details><summary>联网查证（{len(ver)}，其中确认 {sum(1 for v in ver if v.get('resolved_to'))}）</summary>{table(ver, [('识别为', 'as_heard'), ('确认为', 'resolved_to'), ('依据', 'evidence'), ('seg', 'orders')])}</details>
<details><summary>存疑（{len(notes.get('uncertain', []))}）</summary>{table(notes.get('uncertain', []), [('seg', 'orders'), ('问题', 'issue')])}</details>
<details><summary>删掉的非内容（{len(notes.get('removed_non_content', []))}）</summary>{table(notes.get('removed_non_content', []), [('seg', 'orders'), ('内容', 'what')])}</details>
<table class="cmp"><tr><th>原始识别（同传 ASR）</th><th>清稿</th></tr>{''.join(rows)}</table>
</section>"""


def main(root, out_html, *ids):
    root = Path(root)
    if not ids:  # every talk that has finished output, in agenda order
        order = [re.sub(r"[^A-Za-z0-9-]+", "_", t["talk_id"]).strip("_")
                 for t in csv.DictReader((root / "data/01_talks.csv").open(encoding="utf-8"))]
        ids = [f for f in order if (root / f"data/03_clean/{f}.md").exists() and (root / f"data/03_clean/{f}.notes.json").exists()]
    done = [talk_section(root, t) for t in ids]
    sections = [sec for _, sec in done]
    summary = "".join(
        f'<tr class="{"flag" if st["ratio"] < 0.6 or st["uncovered"] or st["q"] >= 15 else ""}"><td><a href="#{st["id"]}">{html.escape(st["talk_id"])}</a></td>'
        f'<td>{html.escape(st["speakers"])}</td><td>{st["ratio"]:.0%}</td><td>{st["paras"]}</td><td>{st["q"]}</td>'
        f'<td>{st["verified"]}</td><td>{st["corrections"]}</td><td>{st["uncovered"]}</td><td>{"是" if st["topic_note"] else ""}</td></tr>'
        for st, _ in done)
    nav = (f'<table class="sum"><tr><th>场次</th><th>讲者</th><th>字符比</th><th>段落</th><th>〔?〕</th><th>联网确认</th>'
           f'<th>纠错</th><th>未覆盖行</th><th>主题≠议程</th></tr>{summary}</table>'
           f'<p class=muted>浅红行：字符比低于 60%、有未覆盖的原文行，或存疑 ≥15 处，建议优先看。</p>')
    page = f"""<!doctype html><html lang="zh"><meta charset="utf-8"><title>清稿对照</title>
<style>
body{{font:14px/1.6 -apple-system,"PingFang SC",sans-serif;margin:24px auto;max-width:1400px;padding:0 16px;color:#222}}
h2 small{{color:#666;font-weight:normal}} .muted{{color:#777;font-size:12px}} .warn{{background:#fff1d6;color:#8a5300;padding:4px 8px;border-radius:6px}}
.kpi{{display:flex;gap:14px;margin:8px 0}} .kpi div{{background:#f5f5f7;padding:6px 12px;border-radius:8px;font-size:12px}} .kpi b{{display:block;font-size:18px}}
table.cmp{{border-collapse:collapse;width:100%;margin-top:12px}} .cmp td,.cmp th{{border-bottom:1px solid #eee;padding:8px;vertical-align:top;text-align:left}}
.cmp td.l{{width:42%;background:#fafafa}} .raw{{font-size:12px;color:#666;line-height:1.45}} .o{{color:#aaa;display:inline-block;width:38px}}
.cmp td.r{{font-size:14.5px}} .rng{{font-size:11px;color:#aaa;margin-top:4px}} tr.h h4{{margin:6px 0;color:#4a6cf7}}
mark.q{{background:#fde7e9;color:#b3261e}} table.mini{{border-collapse:collapse;font-size:12px}} .mini td,.mini th{{border:1px solid #eee;padding:3px 8px}}
section{{border-top:3px solid #4a6cf7;margin-top:36px;padding-top:8px}}
table.sum{{border-collapse:collapse;font-size:12.5px}} .sum td,.sum th{{border-bottom:1px solid #eee;padding:3px 10px;text-align:left}} .sum tr.flag{{background:#fff4f2}}
</style>
<h1>清稿 · 原文对照</h1>
<p><b>这页给谁看</b>：检查校对清稿的质量。左边是现场同传识别的原文（只含嘉宾正文），右边是清稿，按段落对齐。
重点看三件事：专有名词纠得对不对、有没有删掉实质内容、口语清理的程度是否合适。红色 〔?〕 是模型拿不准、没有硬改的地方。</p>
<p>{nav}</p>
{''.join(sections)}
</html>"""
    Path(out_html).write_text(page, encoding="utf-8")
    print("wrote", out_html)


if __name__ == "__main__":
    main(*sys.argv[1:])
