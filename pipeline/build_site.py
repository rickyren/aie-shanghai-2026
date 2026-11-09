"""Build the static site: report (index) -> talk list with tags (talks.html) -> one page per talk.

Usage: .venv/bin/python -I pipeline/build_site.py <project_root> <out_dir>
Inputs: data/05_synthesis/report_body.md, pipeline/landscape_v2.py, pipeline/landscape_svg.py (integration figure),
        data/01_talks.csv, data/04_analysis_v3/*.json, data/03_clean/*.md, data/00_segments.jsonl,
        data/01_segment_labels.jsonl, data/05_synthesis/substance_filter.csv, pipeline/schemas/talk_analysis_v3.json
"""
import csv
import html
import json
import re
import sys
from pathlib import Path

import markdown

sys.path.insert(0, str(Path(__file__).resolve().parent))
import landscape_svg  # noqa: E402  integration figure
import landscape_v2  # noqa: E402  landscape figure

E = html.escape
CITE = re.compile(r"\[((?:d[12][mb]\d{2}|offagenda_[A-Za-z0-9_]+))\]")
SEG = re.compile(r"\[seg\s*(\d+)(?:\s*[–-]\s*(\d+))?\]")

CSS = """
:root{--ink:#1f2328;--sub:#57606a;--muted:#6e7781;--line:#e4e7eb;--blue:#2f5bd3;--blue-bg:#eef3ff;--tag:#f1f4f9}
*{box-sizing:border-box} body{font:15px/1.75 -apple-system,"PingFang SC","Helvetica Neue",sans-serif;color:var(--ink);margin:0;background:#fff}
.wrap{max-width:1040px;margin:0 auto;padding:0 24px 64px}
nav{border-bottom:1px solid var(--line);background:#fff;position:sticky;top:0;z-index:5}
nav .wrap{display:flex;gap:22px;align-items:center;padding-top:12px;padding-bottom:12px}
nav a{color:var(--sub);text-decoration:none;font-size:14px}
.crumb{font-size:13px;color:var(--sub);margin:18px 0 -6px} .crumb a{color:var(--blue);text-decoration:none} .crumb span{margin:0 6px;color:#c9cfd6} nav a.on{color:var(--ink);font-weight:600} nav .brand{color:var(--blue);font-weight:700;margin-right:8px}
h1{font-size:24px;margin:32px 0 8px} h2{font-size:19px;margin:36px 0 10px;padding-bottom:6px;border-bottom:1px solid var(--line)} h3{font-size:16px;margin:26px 0 8px}
a{color:var(--blue)} .muted{color:var(--muted);font-size:13px}
a.cite{font-size:11px;background:var(--blue-bg);color:var(--blue);border-radius:4px;padding:0 4px;text-decoration:none;margin:0 1px;white-space:nowrap}
.infer{color:var(--sub);font-size:12px}
table{border-collapse:collapse;width:100%;font-size:13.5px;margin:10px 0} th,td{border-bottom:1px solid var(--line);padding:7px 8px;text-align:left;vertical-align:top}
th{font-weight:600;color:var(--sub);background:#fafbfc}
.tag{display:inline-block;background:var(--tag);border-radius:5px;padding:0 7px;font-size:12px;color:var(--sub);margin:1px 2px 1px 0;white-space:nowrap}
.tag.pr{background:#fff;border:1px dashed #c9cfd6;color:#8c959f}
blockquote{border-left:3px solid var(--line);margin:8px 0;padding-left:12px;color:var(--sub)}
.seg{color:#aab1b9;font-size:11px;margin-left:4px} details summary{cursor:pointer;color:var(--sub)}
.raw{font-size:12.5px;color:var(--sub);line-height:1.6} .raw .o{display:inline-block;width:48px;color:#aab1b9}
.kv{display:grid;grid-template-columns:110px 1fr;gap:4px 14px;font-size:14px} .kv dt{color:var(--muted)} .kv dd{margin:0}
.core{font-size:16px;font-weight:600;background:var(--blue-bg);padding:10px 14px;border-radius:8px;margin:12px 0}
.filters{display:flex;gap:10px;flex-wrap:wrap;margin:14px 0} .filters input,.filters select{font:inherit;font-size:13.5px;padding:5px 9px;border:1px solid var(--line);border-radius:6px}
tr.row:hover{background:#fafbfc} td .more{display:none} tr.open td .more{display:block;margin-top:6px} th.sort{cursor:pointer}
.figure{margin:16px 0 8px}
"""


# Each talk's place in the landscape figure (layer, group); keeps list/talk pages consistent with the report.
LANDSCAPE = {
    **{f: ("应用", "通用 / 个人 agent") for f in ["d1m13", "d1m10", "d1b01"]},
    **{f: ("应用", "垂直行业") for f in ["d1b02", "d1b12", "d1b06", "d2m02", "d2m03", "d2m06"]},
    **{f: ("应用", "企业内部落地") for f in ["d1m16", "d1m18", "d1b07", "d1b05", "d2m04", "d1b09"]},
    **{f: ("Agent Infra", "搜索与数据 API") for f in ["d1m05", "d1m14", "d2m20"]},
    **{f: ("Agent Infra", "支付与交易") for f in ["d1b04", "d2m12"]},
    **{f: ("Agent Infra", "企业知识与本体") for f in ["d1b08", "d1b10", "d2m19"]},
    **{f: ("Agent Infra", "框架与平台") for f in ["d1b03", "d2m05"]},
    **{f: ("Agent Infra", "身份与权限") for f in ["d1m02", "d2m16"]},
    "d1m12": ("Agent Infra", "沙箱"), "d1m17": ("Agent Infra", "存储"),
    **{f: ("模型", "通用 LLM") for f in ["d1m09", "d1m20", "d2m08"]},
    **{f: ("模型", "端侧 / 决策模型") for f in ["d2m11", "d1m11"]},
    "d2m10": ("模型", "生成模型"),
    **{f: ("模型", "具身与世界模型") for f in ["d2m14", "d2m17", "d2m15", "d2m09", "d2m13", "d2m01"]},
    "d1m07": ("数据与训练", "评测与 RL 数据"),
    **{f: ("数据与训练", "模型与数据 Infra") for f in ["d1m06", "d1m19", "d1m15", "d1m03", "d2m18"]},
    **{f: ("资本与社区", "大会、社区与投资人") for f in ["d1m01", "d1m08", "offagenda_AJ_WaytoAGI", "d2m07"]},
    **{f: ("个人", "独立讲者") for f in ["d1m04", "d1b11"]},
}
LAYER_ORDER = ["应用", "Agent Infra", "模型", "数据与训练", "资本与社区", "个人"]


def short(label):
    return re.split(r"[：（]", label or "")[0]


def page(title, body, active, depth=0):
    up = "../" * depth
    nav = (f'<nav><div class="wrap"><span class="brand">AIE Shanghai 2026</span>'
           f'<a href="{up}index.html" class="{"on" if active == "report" else ""}">报告</a>'
           f'<a href="{up}talks.html" class="{"on" if active == "talks" else ""}">全部分享与打标</a></div></nav>')
    return (f'<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{E(title)}</title><style>{CSS}</style>{nav}<div class="wrap">{body}</div></html>')


def fid_of(talk_id):
    return re.sub(r"[^A-Za-z0-9-]+", "_", talk_id).strip("_")


def link_cites(h, prefix):
    return CITE.sub(lambda m: f'<a class="cite" href="{prefix}talks/{m.group(1)}.html">{m.group(1)}</a>', h)


def build_report(root, talks):
    body = (root / "data/05_synthesis/report_body.md").read_text(encoding="utf-8")
    # figures go in after markdown, so blank lines inside the SVG are not turned into <p> breaks
    figs = {"{{LANDSCAPE}}": (root / "data/05_synthesis/landscape.svg").read_text(encoding="utf-8"), "{{LOOP}}": landscape_svg.loop()}
    h = markdown.markdown(body, extensions=["tables", "sane_lists"])
    for k, svg in figs.items():
        h = h.replace(f"<p>{k}</p>", svg).replace(k, svg)
    h = link_cites(h, "")
    h = h.replace("（推断）", '<span class="infer">（推断）</span>')
    intro = ('<p class="muted">依据现场同传转写整理（53 场 + 展区信息），数字均未核实。方括号编号可跳到单场页；'
             '<a href="talks.html">全部分享与打标</a>汇总了逐场分析。</p>')
    h = h.replace("</h1>", "</h1>" + intro, 1)
    return page("AIE Shanghai 2026：从 53 场分享看 AI 行业", h, "report")


def build_talk_list(talks, analyses, enums, promo):
    lab = lambda k, c: short(enums[k].get(c, c or ""))
    layers = LAYER_ORDER
    rows = []
    for t in talks:
        f = t["fid"]
        a = analyses.get(f, {})
        more = []
        if a.get("skeleton"):
            more.append("<b>骨架</b><ol>" + "".join(f"<li>{E(x)}</li>" for x in a["skeleton"]) + "</ol>")
        if a.get("frameworks"):
            more.append("<b>讲者提出的框架</b><ul>" + "".join(f"<li>{E(x['name'])}：{E(x.get('gist', ''))}</li>" for x in a["frameworks"]) + "</ul>")
        if a.get("offerings"):
            more.append("<b>推出 / 提供</b><ul>" + "".join(f"<li>{E(o['name'])}：{E(o.get('what', ''))}</li>" for o in a["offerings"]) + "</ul>")
        if a.get("why_needed"):
            more.append(f"<b>为什么需要</b><p>{E(a['why_needed'])}</p>")
        if a.get("non_consensus"):
            more.append("<b>非共识</b><ul>" + "".join(f"<li>{E(x['point'])}</li>" for x in a["non_consensus"]) + "</ul>")
        if a.get("signals"):
            more.append("<b>信号</b><ul>" + "".join(f"<li><span class=tag>{E(lab('signal_type', s.get('type')))}</span>{E(s['signal'])}</li>" for s in a["signals"]) + "</ul>")
        tags = " ".join(f'<span class="tag">{E(lab("trend_category", x) if not str(x).startswith("new:") else x[4:])}</span>' for x in a.get("trend_categories", []))
        flag = '<span class="tag pr">偏宣传</span>' if f in promo else ""
        layer, group = LANDSCAPE.get(f, ("其他", ""))
        rows.append(
            f'<tr class="row" data-layer="{E(layer)}" data-text="{E((t["speakers"] + t["orgs"] + t["title"] + a.get("core_message", "")).lower())}">'
            f'<td><a href="talks/{f}.html">{E(t["talk_id"])}</a><div class="muted">{t["day"][5:]} {"主会场" if t["stage"] == "main" else "分会场"}</div></td>'
            f'<td>{E(a.get("speakers") or t["speakers"])}<div class="muted">{E(a.get("org") or t["orgs"])}</div></td>'
            f'<td>{E(layer)}<div class="muted">{E(group)}</div></td>'
            f'<td>{E(a.get("core_message", ""))}<div>{tags} {flag}</div><div class="more">{"".join(more)}</div>'
            f'<a href="#" class="toggle muted" onclick="this.closest(\'tr\').classList.toggle(\'open\');return false;">展开 / 收起明细</a></td>'
            f'<td data-v="{a.get("novelty", 0)}">{a.get("novelty", "")}</td><td data-v="{a.get("pr_level", 0)}">{a.get("pr_level", "")}</td></tr>')
    opts = "".join(f'<option>{E(x)}</option>' for x in layers)
    body = f"""<p class="crumb"><a href="index.html">← 报告</a><span>/</span>全部分享与打标</p><h1>全部分享与打标</h1>
<p class="muted">53 场分享（含 1 场议程外）的逐场分析。打标内容来自校对后的转写，不含原文；点场次编号进入单场页查看完整转写。
「新」= 对资深从业者的新信息量，「PR」= 自家产品推销浓度，均为 1–5 分。「偏宣传」为人工判断，报告的分方向结论未采用这些场次的观点。</p>
<div class="filters"><input id="q" placeholder="搜索讲者、机构、观点…" size="28"><select id="layer"><option value="">全部版图层级</option>{opts}</select></div>
<table id="t"><thead><tr><th>场次</th><th>讲者 / 机构</th><th>版图位置</th><th>核心 message</th><th class="sort" data-col="4">新 ↕</th><th class="sort" data-col="5">PR ↕</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
<script>
const q=document.getElementById('q'),L=document.getElementById('layer');
function f(){{const s=q.value.toLowerCase(),l=L.value;document.querySelectorAll('#t tbody tr').forEach(r=>{{r.style.display=(!s||r.dataset.text.includes(s))&&(!l||r.dataset.layer===l)?'':'none'}})}}
q.oninput=f;L.onchange=f;
document.querySelectorAll('th.sort').forEach(th=>th.onclick=()=>{{const c=+th.dataset.col,tb=document.querySelector('#t tbody'),rs=[...tb.rows];const d=th.dataset.d=th.dataset.d==='1'?'-1':'1';
rs.sort((a,b)=>(+a.cells[c].dataset.v-+b.cells[c].dataset.v)*-d);rs.forEach(r=>tb.appendChild(r))}});
</script>"""
    return page("全部分享与打标 · AIE Shanghai 2026", body, "talks")


def build_talk_page(t, a, enums, clean_md, raw_lines, promo):
    lab = lambda k, c: short(enums[k].get(c, c or ""))
    fm, text = {}, clean_md
    if clean_md.startswith("---"):
        _, head, text = clean_md.split("---", 2)
    text = SEG.sub(lambda m: f'<span class="seg">seg {m.group(1)}{"–" + m.group(2) if m.group(2) else ""}</span>', text)
    clean_h = markdown.markdown(text, extensions=["sane_lists"])
    parts = [f'<p class="crumb"><a href="../index.html">报告</a><span>/</span><a href="../talks.html">全部分享与打标</a><span>/</span>{E(t["talk_id"])}</p>',
             f'<h1>{E(t["title"] or a.get("speakers", ""))}</h1>',
             f'<p class="muted">{E(a.get("speakers") or t["speakers"])} · {E(a.get("org") or t["orgs"])} · {t["day"]} '
             f'{"主会场" if t["stage"] == "main" else "分会场"} · {t["actual_start"]}–{t["actual_end"]} · 场次 {E(t["talk_id"])}'
             f'{" · <span class=\"tag pr\">偏宣传</span>" if t["fid"] in promo else ""}</p>']
    if a:
        parts.append(f'<div class="core">{E(a.get("core_message", ""))}</div>')
        layer, group = LANDSCAPE.get(t["fid"], ("其他", ""))
        kv = [("版图位置", f'{layer} · {group}'), ("细分", a.get("position", "")),
              ("讲者意图", lab("intent", a.get("intent"))), ("客户", lab("target_customer", a.get("target_customer"))),
              ("新信息量 / 推销", f'{a.get("novelty", "")} / {a.get("pr_level", "")}')]
        parts.append('<dl class="kv">' + "".join(f"<dt>{k}</dt><dd>{E(str(v))}</dd>" for k, v in kv) + "</dl>")
        if a.get("skeleton"):
            parts.append("<h3>演讲骨架</h3><ol>" + "".join(f"<li>{E(x)}</li>" for x in a["skeleton"]) + "</ol>")
        if a.get("frameworks"):
            parts.append("<h3>讲者提出的框架</h3><ul>" + "".join(f"<li><b>{E(x['name'])}</b>：{E(x.get('gist', ''))}</li>" for x in a["frameworks"]) + "</ul>")
        if a.get("offerings"):
            parts.append("<h3>推出 / 提供</h3><ul>" + "".join(f"<li><b>{E(o['name'])}</b>：{E(o.get('what', ''))}</li>" for o in a["offerings"]) + "</ul>")
        if a.get("non_consensus"):
            parts.append("<h3>非共识</h3><ul>" + "".join(f"<li>{E(x['point'])}<blockquote>{E(x.get('quote', ''))}</blockquote></li>" for x in a["non_consensus"]) + "</ul>")
        if a.get("signals"):
            parts.append("<h3>信号</h3><ul>" + "".join(f"<li><span class=tag>{E(lab('signal_type', s.get('type')))}</span>{E(s['signal'])}</li>" for s in a["signals"]) + "</ul>")
    parts.append('<h2>转写（校对清稿）</h2><p class="muted">由现场同传语音识别结果校对而成：修正专有名词、去除口头语、合并成段，保留原语言；〔?〕为存疑处。'
                 '数字未经核实。</p>' + clean_h)
    raw = "".join(f'<div><span class="o">{o}</span>{E(x)}</div>' for o, x in raw_lines)
    parts.append(f'<details><summary>原始识别文本（同传 ASR，{len(raw_lines)} 行）</summary><div class="raw">{raw}</div></details>')
    return page(f'{t["talk_id"]} · AIE Shanghai 2026', "".join(parts), "talks", depth=1)


def main(root, out):
    root, out = Path(root), Path(out)
    (out / "talks").mkdir(parents=True, exist_ok=True)
    enums = json.loads((root / "pipeline/schemas/talk_analysis_v3.json").read_text(encoding="utf-8"))["enums"]
    talks = list(csv.DictReader((root / "data/01_talks.csv").open(encoding="utf-8")))
    for t in talks:
        t["fid"] = fid_of(t["talk_id"])
    analyses = {}
    for t in talks:
        p = root / f"data/04_analysis_v3/{t['fid']}.json"
        if p.exists():
            analyses[t["fid"]] = json.loads(p.read_text(encoding="utf-8"))
    promo = {r["file_id"] for r in csv.DictReader((root / "data/05_synthesis/substance_filter.csv").open(encoding="utf-8"))}
    segs = {}
    for line in (root / "data/00_segments.jsonl").open(encoding="utf-8"):
        r = json.loads(line)
        segs[r["seg_id"]] = r
    by_talk = {}
    for line in (root / "data/01_segment_labels.jsonl").open(encoding="utf-8"):
        r = json.loads(line)
        if r["type"] == "talk" and r["session_id"]:
            by_talk.setdefault(fid_of(r["session_id"]), []).append((r["order"], segs[r["seg_id"]]["source_text"]))

    (out / "index.html").write_text(build_report(root, talks), encoding="utf-8")
    (out / "talks.html").write_text(build_talk_list(talks, analyses, enums, promo), encoding="utf-8")
    for t in talks:
        clean = (root / f"data/03_clean/{t['fid']}.md").read_text(encoding="utf-8")
        (out / f"talks/{t['fid']}.html").write_text(
            build_talk_page(t, analyses.get(t["fid"], {}), enums, clean, sorted(by_talk.get(t["fid"], [])), promo), encoding="utf-8")
    (out / ".nojekyll").write_text("")
    print("built", len(talks), "talk pages ->", out)


if __name__ == "__main__":
    main(*sys.argv[1:])
