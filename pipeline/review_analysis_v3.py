"""Validate and render the V3 per-talk analysis (intent + skeleton first, report-oriented fields).

Usage: python3 -I pipeline/review_analysis_v3.py <project_root> <out_html> [<file_id> ...]   (no ids = all in data/04_analysis_v3)
"""
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analysis_validation import validate  # noqa: E402
from review_clean import parse_md  # noqa: E402
from validate_data import read_csv, require_valid  # noqa: E402

DIR = "data/04_analysis_v3"


def card(doc, schema, issues, title):
    e, enums = html.escape, schema["enums"]
    lab = lambda name, code: e(enums[name].get(code, str(code)).split("（")[0])
    seg = lambda x: f' <span class=seg>seg {e(str(x.get("seg", "")))}</span>' if x.get("seg") else ""
    lst = lambda xs: "<ul>" + "".join(f"<li>{x}</li>" for x in xs) + "</ul>" if xs else "<p class=muted>—</p>"
    skeleton = "<ol>" + "".join(f"<li>{e(s)}</li>" for s in doc.get("skeleton", [])) + "</ol>"
    fw = lst([f'<b>{e(f["name"])}</b>：{e(f.get("gist", ""))}{seg(f)}' for f in doc.get("frameworks", [])])
    off = lst([f'<b>{e(o["name"])}</b> <span class=tag>{lab("offering_status", o.get("status"))}</span> {e(o.get("what", ""))}'
               f'<span class=muted> · 给：{e(o.get("for_whom", ""))}</span>' for o in doc.get("offerings", [])])
    pa = lst([f'<b>问题</b>：{e(x["problem"])}<br><b>做法</b>：{e(x["approach"])}' for x in doc.get("problem_approach", [])])
    nc = lst([f'<span class=tag>{lab("nc_kind", p.get("kind"))}</span> {e(p["point"])}'
              f'{" <span class=who>— " + e(p["speaker"]) + "</span>" if p.get("speaker") else ""}'
              f'<details><summary>原句</summary><blockquote>{e(p.get("quote", ""))}{seg(p)}</blockquote></details>'
              for p in doc.get("non_consensus", [])])
    hf = lst([f'<span class=tag>{lab("signal_type", f.get("type"))}</span> {e(f["signal"])}'
              f'{" <span class=muted>（原话数值：" + e(f["value_as_heard"]) + "，转写未核实）</span>" if f.get("value_as_heard") else ""}{seg(f)}'
              for f in doc.get("signals", [])])
    trends = "、".join(lab("trend_category", t) if not str(t).startswith("new:") else e(t) for t in doc.get("trend_categories", []))
    return f"""<section id="{e(doc['_fid'])}">
<div class=head><b>{e(doc.get('talk_id', ''))}</b> · {e(doc.get('speakers', ''))} · <b>{e(doc.get('org', ''))}</b>
<span class=tag>{lab('value_chain_layer', doc.get('value_chain_layer'))} · {e(doc.get('position', ''))}</span>
<span class=tag>客户：{lab('target_customer', doc.get('target_customer'))}</span>
<span class="tag intent">{lab('intent', doc.get('intent'))}</span>
<span class=score title="新信息量 / 推销浓度">新 {doc.get('novelty')} · PR {doc.get('pr_level')}</span>
<div class=muted>{e(title)}</div></div>
{''.join(f'<p class=warn>{e(i)}</p>' for i in issues)}
<p class=core>{e(doc.get('core_message', ''))}</p>
<div class=grid>
<div><h4>演讲骨架</h4>{skeleton}<h4>讲者提出的框架</h4>{fw}</div>
<div><h4>推出 / 提供</h4>{off}<h4>为什么需要它</h4><p>{e(doc.get('why_needed', '')) or '<span class=muted>—</span>'}</p></div>
</div>
<div class=grid>
<div><h4>问题 → 做法</h4>{pa}<h4>非共识</h4>{nc}</div>
<div><h4>信号（数据 / 市场格局 / 关注的指标 / 发布）</h4>{hf}
{f'<h4>内容行业</h4><p class=content>{e(doc["content_industry_note"])}</p>' if doc.get('content_industry_note') else ''}</div>
</div>
<p class=muted>趋势：{trends} · 已过滤的共识：{e("；".join(doc.get('filtered_consensus', [])))}</p>
</section>"""


def landscape_table(docs, schema):
    """Talks grouped by value-chain layer: org, position, what they offer, core message (draft for the landscape)."""
    if len(docs) < 2:
        return ""
    e, enums = html.escape, schema["enums"]
    rows = []
    for layer, label in enums["value_chain_layer"].items():
        group = [d for d in docs if d.get("value_chain_layer") == layer]
        if not group:
            continue
        rows.append(f'<tr class=grp><td colspan=4>{e(label)}（{len(group)}）</td></tr>')
        for d in group:
            offer = "；".join(o["name"] for o in d.get("offerings", [])) or "—"
            rows.append(f'<tr><td><a href="#{e(d["_fid"])}">{e(d.get("org", ""))}</a><div class=muted>{e(d.get("talk_id", ""))}</div></td>'
                        f'<td>{e(d.get("position", ""))}</td><td>{e(offer)}</td><td>{e(d.get("core_message", ""))}</td></tr>')
    return (f'<h2>按产业链层级分组（landscape 底稿）</h2><table class=land><tr><th>机构</th><th>细分位置</th><th>推出 / 提供</th><th>核心 message</th></tr>'
            f'{"".join(rows)}</table><h2>逐场精要</h2>')


def main(root, out_html, *ids):
    root = Path(root)
    if not ids:
        require_valid(root)
    schema = json.loads((root / "pipeline/schemas/talk_analysis_v3.json").read_text(encoding="utf-8"))
    titles = {re.sub(r"[^A-Za-z0-9-]+", "_", t["talk_id"]).strip("_"): t["title"]
              for t in read_csv(root / "data/01_talks.csv")}
    if not ids:  # agenda order
        ids = [f for f in titles if (root / f"{DIR}/{f}.json").exists()]
    cards, report, docs = [], {}, []
    for fid in ids:
        doc = json.loads((root / f"{DIR}/{fid}.json").read_text(encoding="utf-8"))
        _, blocks = parse_md((root / f"data/03_clean/{fid}.md").read_text(encoding="utf-8"))
        issues = validate(doc, schema, [b for b in blocks if b[0] == "p" and b[2]])
        report[fid] = issues
        if issues:
            cards.append(f'<section><h2>{html.escape(fid)}</h2>'
                         + "".join(f'<p class="warn">{html.escape(issue)}</p>' for issue in issues) + '</section>')
            continue
        doc["_fid"] = fid  # presentation metadata is not part of the analysis schema
        docs.append(doc)
        cards.append(card(doc, schema, issues, titles.get(fid, "")))
    landscape = landscape_table(docs, schema)
    page = f"""<!doctype html><html lang="zh"><meta charset="utf-8"><title>单场精要 V3</title>
<style>
body{{font:14.5px/1.65 -apple-system,"PingFang SC",sans-serif;margin:24px auto;max-width:1150px;padding:0 16px;color:#222}}
section{{border:1px solid #e6e6e6;border-radius:12px;padding:14px 18px;margin:18px 0}}
.tag{{display:inline-block;background:#f1f3f4;border-radius:10px;padding:0 8px;margin-left:4px;font-size:12px;color:#444}} .tag.intent{{background:#e3e9ff}}
.score{{float:right;font-size:12px;color:#666}} .core{{font-size:16.5px;font-weight:600;margin:10px 0;line-height:1.6;background:#f4f6ff;padding:8px 12px;border-radius:8px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:22px}} h4{{margin:8px 0 2px;color:#4a6cf7;font-size:13px}} ul,ol{{margin:0;padding-left:20px}}
blockquote{{margin:2px 0;padding-left:10px;border-left:3px solid #ddd;color:#555;font-size:13px}} .seg{{color:#aaa;font-size:11px}}
.who{{color:#888;font-size:12px}} .muted{{color:#888;font-size:12px}} .content{{background:#f4fbf6;padding:6px 10px;border-radius:8px;font-size:13.5px;margin:0}}
.warn{{background:#fff1d6;color:#8a5300;padding:3px 8px;border-radius:6px;font-size:12px}}
table.land{{border-collapse:collapse;width:100%;font-size:13px}} .land td,.land th{{border-bottom:1px solid #eee;padding:5px 8px;vertical-align:top;text-align:left}}
.land tr.grp td{{background:#f4f6ff;font-weight:600;color:#4a6cf7}} details summary{{font-size:11px;color:#999;cursor:pointer}}
</style>
<h1>单场精要 V3</h1>
<p class=muted>先还原讲者为什么上台、整场骨架是什么，再给出核心 message；产品类分享会写明“推出了什么”和“在已有替代方案的情况下为什么还需要它”。
非共识最多 3 条、信号最多 4 条，没有就留空。数字来自语音转写、未经核实，只作为“讲者在关注什么指标”的参考。“新 / PR” 是 1–5 分的新信息量和推销浓度。</p>
{landscape}
{''.join(cards)}</html>"""
    Path(out_html).write_text(page, encoding="utf-8")
    print("wrote", out_html, {k: len(v) for k, v in report.items()})
    for k, v in report.items():
        for i in v:
            print(" ", k, i)
    if any(report.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main(*sys.argv[1:])
