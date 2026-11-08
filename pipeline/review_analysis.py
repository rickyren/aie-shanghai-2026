"""Validate per-talk analysis JSON against the schema and the clean transcript, and render a review page.

Usage: python3 -I pipeline/review_analysis.py <project_root> <out_html> [<file_id> ...]   (no ids = all analysed talks)
"""
import html
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from review_clean import parse_md  # noqa: E402

NORM = re.compile(r"[\s*`\"“”'‘’「」『』]+")


def norm(s):
    return NORM.sub("", s or "")


def seg_range(s):
    m = re.match(r"\s*(\d+)\s*(?:[–-]\s*(\d+))?\s*$", str(s or ""))
    return (int(m.group(1)), int(m.group(2) or m.group(1))) if m else None


def validate(doc, enums, paras):
    """-> list of issue strings."""
    issues = []
    full = norm("".join(t for _, t, _ in paras))

    def enum(val, name, where):
        if val is not None and val not in enums[name]:
            issues.append(f"{where}: 非法取值 {val!r}")

    org = doc.get("org", {})
    enum(org.get("value_chain_layer"), "value_chain_layer", "org.value_chain_layer")
    enum(org.get("org_type"), "org_type", "org.org_type")
    tt = doc.get("talk_type", {})
    enum(tt.get("primary"), "talk_type", "talk_type.primary")
    enum(tt.get("secondary"), "talk_type", "talk_type.secondary")
    for c in doc.get("key_claims", []):
        enum(c.get("kind"), "claim_kind", "key_claims.kind")
    for p in doc.get("practices", []):
        enum(p.get("outcome"), "practice_outcome", "practices.outcome")
    for s in doc.get("signals", []):
        enum(s.get("type"), "signal_type", "signals.type")
    for e in doc.get("entities", []):
        enum(e.get("kind"), "entity_kind", "entities.kind")
        enum(e.get("role"), "entity_role", "entities.role")
    for t in doc.get("trend_categories", []):
        if not str(t).startswith("new:"):
            enum(t, "trend_category", "trend_categories")
    lo = min(r[0] for _, _, r in paras)
    hi = max(r[1] for _, _, r in paras)
    for field in ("key_claims", "quotable"):
        for i, c in enumerate(doc.get(field, [])):
            q = norm(c.get("quote"))
            if not q:
                issues.append(f"{field}[{i}]: 缺少引用")
            elif q not in full:
                issues.append(f"{field}[{i}]: 引用在清稿中找不到 —— {c.get('quote', '')[:40]}")
            else:
                r = seg_range(c.get("seg"))
                home = [pr for _, t, pr in paras if q in norm(t)]
                if r and home and not any(pr[0] <= r[1] and pr[1] >= r[0] for pr in home):
                    issues.append(f"{field}[{i}]: seg {c.get('seg')} 与引用所在段落 {home[0][0]}–{home[0][1]} 不一致")
    for field in ("practices", "pain_points", "predictions", "signals"):
        for i, c in enumerate(doc.get(field, [])):
            r = seg_range(c.get("seg"))
            if not r or r[0] < lo or r[1] > hi:
                issues.append(f"{field}[{i}]: seg {c.get('seg')!r} 不在本场范围 {lo}–{hi}")
    return issues


def render_talk(doc, enums, issues):
    e = html.escape
    lab = lambda name, code: e(enums[name].get(code, code or "—").split("（")[0]) if code else "—"

    def items(field, fmt):
        xs = doc.get(field, [])
        return "<ul>" + "".join(f"<li>{fmt(x)}</li>" for x in xs) + "</ul>" if xs else "<p class=muted>无</p>"

    by_sig = {}
    for s in doc.get("signals", []):
        by_sig.setdefault(s.get("type"), []).append(s)
    signals = "".join(
        f"<div><b>{lab('signal_type', t)}</b><ul>" + "".join(f"<li>{e(s['detail'])} <span class=seg>{e(str(s.get('seg', '')))}</span></li>" for s in xs) + "</ul></div>"
        for t, xs in by_sig.items()) or "<p class=muted>无</p>"
    ents = Counter(x.get("role") for x in doc.get("entities", []))
    ent_html = " ".join(f'<span class="ent {e(x.get("role", ""))}" title="{lab("entity_kind", x.get("kind"))} · {lab("entity_role", x.get("role"))}">{e(x.get("name", ""))}</span>'
                        for x in doc.get("entities", []))
    org = doc.get("org", {})
    return f"""<section id="{e(doc['_fid'])}">
<h2>{e(doc.get('talk_id', ''))} · {e(org.get('name', ''))} <small>{e(doc.get('actual_title', ''))}</small></h2>
{''.join(f'<p class=warn>{e(i)}</p>' for i in issues)}
<div class=grid>
<div><b>产业链位置</b>：{lab('value_chain_layer', org.get('value_chain_layer'))} / {e(org.get('sub_layer', ''))}<br>
<span class=muted>{e(org.get('one_liner', ''))}<br>归类理由：{e(org.get('layer_rationale', ''))}</span></div>
<div><b>分享类型</b>：{lab('talk_type', doc.get('talk_type', {}).get('primary'))}{' + ' + lab('talk_type', doc['talk_type'].get('secondary')) if doc.get('talk_type', {}).get('secondary') else ''}<br>
<b>趋势分类</b>：{'、'.join(lab('trend_category', t) if not str(t).startswith('new:') else e(t) for t in doc.get('trend_categories', []))}<br>
<b>打分</b>：信息密度 {doc.get('scores', {}).get('info_density')} · 新颖度 {doc.get('scores', {}).get('novelty')} · PR 浓度 {doc.get('scores', {}).get('pr_level')}
<span class=muted>（{e(doc.get('scores', {}).get('rationale', ''))}）</span></div></div>
<p class=core>{e(doc.get('core_message', ''))}</p>
<p>{e(doc.get('summary', ''))}</p>
<h4>核心论点</h4>{items('key_claims', lambda c: f"<b>[{lab('claim_kind', c.get('kind'))}]</b> {e(c.get('claim', ''))}<blockquote>{e(c.get('quote', ''))} <span class=seg>{e(str(c.get('seg', '')))}</span></blockquote>")}
<div class=grid>
<div><h4>实践（做法 → 效果）</h4>{items('practices', lambda p: f"<b>[{lab('practice_outcome', p.get('outcome'))}]</b> {e(p.get('practice', ''))}{' · 条件：' + e(p['conditions']) if p.get('conditions') else ''} <span class=seg>{e(str(p.get('seg', '')))}</span>")}</div>
<div><h4>痛点</h4>{items('pain_points', lambda p: f"{e(p.get('problem', ''))} <span class=seg>{e(str(p.get('seg', '')))}</span>")}
<h4>预测</h4>{items('predictions', lambda p: f"{e(p.get('prediction', ''))}{' · ' + e(p['horizon']) if p.get('horizon') else ''} <span class=seg>{e(str(p.get('seg', '')))}</span>")}</div></div>
<h4>信号</h4><div class=sig>{signals}</div>
<h4>提到的公司 / 产品（{sum(ents.values())}）</h4><div>{ent_html}</div>
<h4>金句</h4>{items('quotable', lambda q: f"{e(q.get('quote', ''))} <span class=seg>{e(str(q.get('seg', '')))}</span>")}
<h4>对内容行业</h4><p>{e(doc.get('content_industry_note', '')) or '<span class=muted>（无）</span>'}</p>
</section>"""


def main(root, out_html, *ids):
    root = Path(root)
    enums = json.loads((root / "pipeline/schemas/talk_analysis.json").read_text(encoding="utf-8"))["enums"]
    ids = ids or sorted(p.stem for p in (root / "data/04_analysis").glob("*.json"))
    rows, cards, all_issues = [], [], {}
    for fid in ids:
        doc = json.loads((root / f"data/04_analysis/{fid}.json").read_text(encoding="utf-8"))
        doc["_fid"] = fid
        _, blocks = parse_md((root / f"data/03_clean/{fid}.md").read_text(encoding="utf-8"))
        paras = [b for b in blocks if b[0] == "p" and b[2]]
        issues = validate(doc, enums, paras)
        all_issues[fid] = issues
        org, sc = doc.get("org", {}), doc.get("scores", {})
        lab = lambda name, code: html.escape(enums[name].get(code, code or "—").split("（")[0]) if code else "—"
        rows.append(f'<tr class="{"bad" if issues else ""}"><td><a href="#{fid}">{html.escape(doc.get("talk_id", fid))}</a></td>'
                    f'<td>{html.escape(org.get("name", ""))}</td><td>{lab("value_chain_layer", org.get("value_chain_layer"))}</td>'
                    f'<td>{lab("talk_type", doc.get("talk_type", {}).get("primary"))}</td>'
                    f'<td>{html.escape(doc.get("core_message", ""))}</td>'
                    f'<td>{sc.get("info_density")}/{sc.get("novelty")}/{sc.get("pr_level")}</td>'
                    f'<td>{len(doc.get("signals", []))}（数据 {sum(s.get("type") == "data" for s in doc.get("signals", []))}）</td>'
                    f'<td>{len(issues)}</td></tr>')
        cards.append(render_talk(doc, enums, issues))
    page = f"""<!doctype html><html lang="zh"><meta charset="utf-8"><title>单场分析 · 打标结果</title>
<style>
body{{font:14px/1.6 -apple-system,"PingFang SC",sans-serif;margin:24px auto;max-width:1300px;padding:0 16px;color:#222}}
table.sum{{border-collapse:collapse;width:100%;font-size:13px}} .sum td,.sum th{{border-bottom:1px solid #eee;padding:6px 8px;text-align:left;vertical-align:top}} .sum tr.bad{{background:#fff4f2}}
section{{border-top:3px solid #4a6cf7;margin-top:32px;padding-top:6px}} h2 small{{color:#666;font-weight:normal;font-size:14px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px}} .muted{{color:#777;font-size:12px}} .core{{font-size:16px;font-weight:600;background:#f4f6ff;padding:8px 12px;border-radius:8px}}
blockquote{{margin:2px 0 6px 0;padding-left:10px;border-left:3px solid #ddd;color:#555;font-size:13px}} .seg{{color:#aaa;font-size:11px}}
.warn{{background:#fff1d6;color:#8a5300;padding:3px 8px;border-radius:6px;font-size:12px;margin:2px 0}}
.ent{{display:inline-block;background:#f1f3f4;border-radius:10px;padding:0 8px;margin:2px;font-size:12px}} .ent.self{{background:#e3e9ff}} .ent.customer{{background:#e6f4ea}} .ent.competitor{{background:#fde7e9}}
.sig{{display:grid;grid-template-columns:1fr 1fr;gap:6px 20px}} h4{{margin:12px 0 4px}}
</style>
<h1>单场分析 · 打标结果</h1>
<p><b>这页给谁看</b>：检查打标质量和标签维度是否合适。顶部总表一行一场；点场次名看完整分析。所有论点都附清稿原句和段落编号，
校验脚本会自动核对引用是否真实存在于清稿中（浅红行表示有校验问题）。打分格式：信息密度/新颖度/PR 浓度（1–5）。
实体颜色：蓝=讲者自家，绿=客户，红=竞品，灰=其他。</p>
<table class=sum><tr><th>场次</th><th>机构</th><th>产业链位置</th><th>分享类型</th><th>核心观点</th><th>打分</th><th>信号</th><th>校验问题</th></tr>{''.join(rows)}</table>
{''.join(cards)}</html>"""
    Path(out_html).write_text(page, encoding="utf-8")
    print("wrote", out_html, {k: len(v) for k, v in all_issues.items()})
    for k, v in all_issues.items():
        for i in v[:5]:
            print(" ", k, i)


if __name__ == "__main__":
    main(*sys.argv[1:])
