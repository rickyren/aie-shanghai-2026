"""Validate and render the lean (V2) per-talk analysis.

Usage: python3 -I pipeline/review_analysis_v2.py <project_root> <out_html> [<file_id> ...]   (no ids = all in data/04_analysis_v2)
"""
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from review_analysis import norm, seg_range  # noqa: E402
from review_clean import parse_md  # noqa: E402

DIR = "data/04_analysis_v2"


def validate(doc, schema, paras):
    enums, limits = schema["enums"], schema["limits"]
    issues = []
    full = norm("".join(t for _, t, _ in paras))
    lo, hi = min(r[0] for _, _, r in paras), max(r[1] for _, _, r in paras)
    for key, name in (("value_chain_layer", "value_chain_layer"), ("message_type", "message_type")):
        if doc.get(key) not in enums[name]:
            issues.append(f"{key}: 非法取值 {doc.get(key)!r}")
    for t in doc.get("trend_categories", []):
        if not str(t).startswith("new:") and t not in enums["trend_category"]:
            issues.append(f"trend_categories: 非法取值 {t!r}")
    for f in doc.get("hard_facts", []):
        if f.get("type") not in enums["fact_type"]:
            issues.append(f"hard_facts.type: 非法取值 {f.get('type')!r}")
    for field, cap in limits.items():
        if len(doc.get(field, [])) > cap:
            issues.append(f"{field}: {len(doc[field])} 条，超过上限 {cap}")
    for i, p in enumerate(doc.get("non_consensus", [])):
        if norm(p.get("quote")) not in full:
            issues.append(f"non_consensus[{i}]: 引用在清稿中找不到")
    for field in ("non_consensus", "hard_facts"):
        for i, p in enumerate(doc.get(field, [])):
            r = seg_range(p.get("seg"))
            if not r or r[0] < lo or r[1] > hi:
                issues.append(f"{field}[{i}]: seg {p.get('seg')!r} 不在 {lo}–{hi}")
    return issues


def card(doc, schema, issues):
    e, enums = html.escape, schema["enums"]
    lab = lambda name, code: e(enums[name].get(code, str(code)).split("（")[0])
    nc = "".join(f'<li>{e(p["point"])}{" <span class=who>— " + e(p["speaker"]) + "</span>" if p.get("speaker") else ""}'
                 f'<details><summary>原句</summary><blockquote>{e(p.get("quote", ""))} <span class=seg>seg {e(str(p.get("seg", "")))}</span></blockquote></details></li>'
                 for p in doc.get("non_consensus", [])) or "<li class=muted>无——这场没有超出共识的内容</li>"
    hf = "".join(f'<li><span class=tag>{lab("fact_type", f.get("type"))}</span> {e(f["fact"])} <span class=seg>seg {e(str(f.get("seg", "")))}</span></li>'
                 for f in doc.get("hard_facts", [])) or "<li class=muted>无</li>"
    trends = "、".join(lab("trend_category", t) if not str(t).startswith("new:") else e(t) for t in doc.get("trend_categories", []))
    return f"""<section id="{e(doc['_fid'])}">
<div class=head><b>{e(doc.get('talk_id', ''))}</b> · {e(doc.get('speakers', ''))} · <b>{e(doc.get('org', ''))}</b>
<span class=tag>{lab('value_chain_layer', doc.get('value_chain_layer'))} · {e(doc.get('position', ''))}</span>
<span class=tag>{lab('message_type', doc.get('message_type'))}</span>
<span class=score title="新信息量 / PR 浓度">新 {doc.get('novelty')} · PR {doc.get('pr_level')}</span></div>
{''.join(f'<p class=warn>{e(i)}</p>' for i in issues)}
<p class=core>{e(doc.get('core_message', ''))}</p>
<div class=grid><div><h4>非共识</h4><ul>{nc}</ul></div><div><h4>硬信息</h4><ul>{hf}</ul></div></div>
{f'<p class=content><b>内容行业：</b>{e(doc["content_industry_note"])}</p>' if doc.get('content_industry_note') else ''}
<p class=muted>趋势：{trends} · 已过滤的共识：{e("；".join(doc.get('filtered_consensus', [])))}</p>
</section>"""


def main(root, out_html, *ids):
    root = Path(root)
    schema = json.loads((root / "pipeline/schemas/talk_analysis_v2.json").read_text(encoding="utf-8"))
    ids = ids or sorted(p.stem for p in (root / DIR).glob("*.json"))
    cards, report = [], {}
    for fid in ids:
        doc = json.loads((root / f"{DIR}/{fid}.json").read_text(encoding="utf-8"))
        doc["_fid"] = fid
        _, blocks = parse_md((root / f"data/03_clean/{fid}.md").read_text(encoding="utf-8"))
        issues = validate(doc, schema, [b for b in blocks if b[0] == "p" and b[2]])
        report[fid] = issues
        cards.append(card(doc, schema, issues))
    page = f"""<!doctype html><html lang="zh"><meta charset="utf-8"><title>单场精要</title>
<style>
body{{font:14.5px/1.65 -apple-system,"PingFang SC",sans-serif;margin:24px auto;max-width:1100px;padding:0 16px;color:#222}}
section{{border:1px solid #e6e6e6;border-radius:12px;padding:14px 18px;margin:18px 0}} .head{{font-size:14px}}
.tag{{display:inline-block;background:#f1f3f4;border-radius:10px;padding:0 8px;margin-left:6px;font-size:12px;color:#444}}
.score{{float:right;font-size:12px;color:#666}} .core{{font-size:16.5px;font-weight:600;margin:10px 0;line-height:1.6}}
.grid{{display:grid;grid-template-columns:1.3fr 1fr;gap:20px}} h4{{margin:4px 0;color:#4a6cf7;font-size:13px}} ul{{margin:0;padding-left:18px}}
blockquote{{margin:2px 0;padding-left:10px;border-left:3px solid #ddd;color:#555;font-size:13px}} .seg{{color:#aaa;font-size:11px}}
.who{{color:#888;font-size:12px}} .muted{{color:#888;font-size:12px}} .content{{background:#f4fbf6;padding:6px 10px;border-radius:8px;font-size:13.5px}}
.warn{{background:#fff1d6;color:#8a5300;padding:3px 8px;border-radius:6px;font-size:12px}} details summary{{font-size:11px;color:#999;cursor:pointer}}
</style>
<h1>单场精要</h1>
<p class=muted>每场只保留讲者最想传递的一个 message、超出业内共识的 0–3 条内容和 0–3 条硬信息；被视为共识而删掉的内容列在卡片底部，方便核对过滤是否合理。“新 / PR” 是 1–5 分的新信息量和推销浓度。</p>
{''.join(cards)}</html>"""
    Path(out_html).write_text(page, encoding="utf-8")
    print("wrote", out_html, {k: len(v) for k, v in report.items()})
    for k, v in report.items():
        for i in v:
            print(" ", k, i)


if __name__ == "__main__":
    main(*sys.argv[1:])
