"""Build the static site: report (index) -> talk list with tags (talks.html) -> one page per talk.

Usage: .venv/bin/python -I pipeline/build_site.py <project_root> <out_dir>
Inputs: data/05_synthesis/report_body.md, data/05_synthesis/landscape.svg, data/05_synthesis/landscape.json, pipeline/landscape_svg.py (integration figure),
        data/01_talks.csv, data/04_analysis_v3/*.json, data/03_clean/*.md, data/00_segments.jsonl,
        data/01_segment_labels.jsonl, data/05_synthesis/substance_filter.csv, pipeline/schemas/talk_analysis_v3.json
"""
import html
import json
import re
import shutil
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import markdown

sys.path.insert(0, str(Path(__file__).resolve().parent))
import landscape_svg  # noqa: E402  integration figure
from landscape import load_landscape, talk_positions  # noqa: E402
from analysis_validation import seg_range  # noqa: E402
from check_site import check_site  # noqa: E402
from review_clean import parse_md  # noqa: E402
from validate_data import file_id, read_csv, read_jsonl, require_valid  # noqa: E402

E = html.escape
CITE = re.compile(r"\[((?:d[12][mb]\d{2}|offagenda_[A-Za-z0-9_]+))\]")

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
.seg{color:var(--sub);font-size:11px;margin-left:4px} details summary{cursor:pointer;color:var(--sub)}
.transcript-paragraph,.raw div{scroll-margin-top:90px}.transcript-paragraph:target{background:#fff8dc;border-radius:6px;padding:4px 10px}
.transcript-paragraph p{margin-bottom:0}.transcript-paragraph{margin-bottom:18px}
.toggle{border:0;background:none;padding:0;color:var(--blue);cursor:pointer;font:inherit;font-size:13px}
.raw{font-size:12.5px;color:var(--sub);line-height:1.6} .raw .o{display:inline-block;width:48px;color:#aab1b9}
.kv{display:grid;grid-template-columns:135px 1fr;gap:4px 14px;font-size:14px} .kv dt{color:var(--muted)} .kv dd{margin:0}
.core{font-size:16px;font-weight:600;background:var(--blue-bg);padding:10px 14px;border-radius:8px;margin:12px 0}
.filters{display:flex;gap:10px;flex-wrap:wrap;margin:14px 0} .filters input,.filters select{font:inherit;font-size:13.5px;padding:5px 9px;border:1px solid var(--line);border-radius:6px}
tr.row:hover{background:#fafbfc} td .more{display:none} tr.open td .more{display:block;margin-top:6px} th.sort{cursor:pointer}
.figure{margin:16px 0 8px}
@media(max-width:640px){.wrap{padding-left:14px;padding-right:14px}nav .wrap{gap:14px;flex-wrap:wrap}.table-scroll{overflow-x:auto}.table-scroll table{min-width:760px}.kv{grid-template-columns:90px 1fr}}
"""



def short(label):
    return re.split(r"[：（]", label or "")[0]


def page(title, body, active, depth=0):
    up = "../" * depth
    nav = (f'<nav><div class="wrap"><span class="brand">AIE Shanghai 2026</span>'
           f'<a href="{up}index.html" class="{"on" if active == "report" else ""}">参会笔记</a>'
           f'<a href="{up}talks.html" class="{"on" if active == "talks" else ""}">全部演讲</a></div></nav>')
    return (f'<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{E(title)}</title><style>{CSS}</style>{nav}<div class="wrap">{body}</div></html>')


def fid_of(talk_id):
    return file_id(talk_id)


def link_cites(h, prefix):
    return CITE.sub(lambda m: f'<a class="cite" href="{prefix}talks/{m.group(1)}.html">{m.group(1)}</a>', h)


def evidence_link(item, paras, prefix=""):
    span = seg_range(item["seg"])
    target = next(a for _, _, (a, b) in paras if a <= span[1] and b >= span[0])
    return f' <a class="seg" href="{prefix}#seg-{target}">查看原文</a>'


def render_transcript(clean_md, raw_orders):
    _, blocks = parse_md(clean_md)
    result, seen = [], set()
    for kind, text, span in blocks:
        if kind == "h":
            # parse_md removes heading markers; preserve the heading's text.
            result.append(f"<h3>{E(text)}</h3>")
            continue
        start, end = span
        anchor = f' id="seg-{start}"' if start not in seen else ""
        seen.add(start)
        raw_start = next((order for order in raw_orders if start <= order <= end), None)
        raw_link = (f'<a class="seg" href="#raw-{raw_start}">识别文本 {start}–{end}</a>'
                    if raw_start is not None else "")
        result.append(f'<div class="transcript-paragraph"{anchor}>'
                      + markdown.markdown(text, extensions=["sane_lists"]) + raw_link + "</div>")
    return "".join(result)


def build_report(root):
    body = (root / "data/05_synthesis/report_body.md").read_text(encoding="utf-8")
    # figures go in after markdown, so blank lines inside the SVG are not turned into <p> breaks
    figs = {"{{LANDSCAPE}}": (root / "data/05_synthesis/landscape.svg").read_text(encoding="utf-8"), "{{LOOP}}": landscape_svg.loop()}
    h = markdown.markdown(body, extensions=["tables", "sane_lists"])
    for k, svg in figs.items():
        h = h.replace(f"<p>{k}</p>", svg).replace(k, svg)
    h = link_cites(h, "")
    h = h.replace("（推断）", '<span class="infer">（推断）</span>')
    intro = ('<p class="muted">2026 年 11 月 5–6 日，上海。整理了 53 场演讲和部分展商资料。数字来自语音识别，尚未核实。点击文中的场次编号可查看原文。'
             '<a href="talks.html">查找演讲 →</a></p>')
    h = h.replace("</h1>", "</h1>" + intro, 1)
    return page("AIE Shanghai 2026 参会笔记", h, "report")


def build_talk_list(talks, analyses, enums, promo, positions, paras_by_id):
    lab = lambda k, c: short(enums[k].get(c, c or ""))
    layers = list(dict.fromkeys(layer for layer, _ in positions.values()))
    rows = []
    for t in talks:
        f = t["fid"]
        a = analyses[f]
        cite = lambda item: evidence_link(item, paras_by_id[f], f"talks/{f}.html")
        more = []
        if a.get("skeleton"):
            more.append("<b>演讲提纲</b><ol>" + "".join(f"<li>{E(x)}</li>" for x in a["skeleton"]) + "</ol>")
        if a.get("frameworks"):
            more.append("<b>讲者提出的框架</b><ul>" + "".join(f"<li>{E(x['name'])}：{E(x.get('gist', ''))}{cite(x)}</li>" for x in a["frameworks"]) + "</ul>")
        if a.get("offerings"):
            more.append("<b>产品与服务</b><ul>" + "".join(f"<li>{E(o['name'])}：{E(o.get('what', ''))}</li>" for o in a["offerings"]) + "</ul>")
        if a.get("why_needed"):
            more.append(f"<b>为什么需要</b><p>{E(a['why_needed'])}</p>")
        if a.get("non_consensus"):
            more.append("<b>非共识</b><ul>" + "".join(f"<li>{E(x['point'])}{cite(x)}</li>" for x in a["non_consensus"]) + "</ul>")
        if a.get("signals"):
            more.append("<b>信号</b><ul>" + "".join(f"<li><span class=tag>{E(lab('signal_type', s.get('type')))}</span>{E(s['signal'])}{cite(s)}</li>" for s in a["signals"]) + "</ul>")
        tags = " ".join(f'<span class="tag">{E(lab("trend_category", x) if not str(x).startswith("new:") else x[4:])}</span>' for x in a.get("trend_categories", []))
        flag = '<span class="tag pr">偏宣传</span>' if f in promo else ""
        layer, group = positions[f]
        rows.append(
            f'<tr class="row" data-layer="{E(layer)}" data-text="{E(" ".join((t["talk_id"], t["speakers"], t["orgs"], a["speakers"], a["org"], t["title"], a["core_message"])).lower())}">'
            f'<td><a href="talks/{f}.html">{E(t["talk_id"])}</a><div class="muted">{t["day"][5:]} {"主会场" if t["stage"] == "main" else "分会场"}</div></td>'
            f'<td>{E(a.get("speakers") or t["speakers"])}<div class="muted">{E(a.get("org") or t["orgs"])}</div></td>'
            f'<td>{E(layer)}<div class="muted">{E(group)}</div></td>'
            f'<td>{E(a.get("core_message", ""))}<div>{tags} {flag}</div><div class="more">{"".join(more)}</div>'
            f'<button type="button" class="toggle" aria-expanded="false" onclick="const open=this.closest(\'tr\').classList.toggle(\'open\');this.setAttribute(\'aria-expanded\',open);this.textContent=open?\'收起详情\':\'展开详情\'">展开详情</button></td>'
            f'<td data-v="{a.get("novelty", 0)}">{a.get("novelty", "")}</td><td data-v="{a.get("pr_level", 0)}">{a.get("pr_level", "")}</td></tr>')
    opts = "".join(f'<option>{E(x)}</option>' for x in layers)
    body = f"""<p class="crumb"><a href="index.html">← 参会笔记</a><span>/</span>全部演讲</p><h1>全部演讲</h1>
<p class="muted">共 53 场，含 1 场议程外分享。点击场次编号可看摘要和完整转写。
「新信息量」指对资深从业者的新信息量，「推销浓度」指自家产品的推销程度，均为 1–5 分。标为「偏宣传」的场次不作为分方向结论的观点依据。</p>
<div class="filters"><input id="q" aria-label="搜索演讲" placeholder="搜索讲者、机构、观点…" size="28"><select id="layer" aria-label="按版图位置筛选"><option value="">全部版图层级</option>{opts}</select></div>
<div class="table-scroll"><table id="t"><thead><tr><th>场次</th><th>讲者 / 机构</th><th>版图位置</th><th>主要观点</th><th class="sort" data-col="4">新信息量 ↕</th><th class="sort" data-col="5">推销浓度 ↕</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>
<script>
const q=document.getElementById('q'),L=document.getElementById('layer');
function f(){{const s=q.value.toLowerCase(),l=L.value;document.querySelectorAll('#t tbody tr').forEach(r=>{{r.style.display=(!s||r.dataset.text.includes(s))&&(!l||r.dataset.layer===l)?'':'none'}})}}
q.oninput=f;L.onchange=f;
document.querySelectorAll('th.sort').forEach(th=>th.onclick=()=>{{const c=+th.dataset.col,tb=document.querySelector('#t tbody'),rs=[...tb.rows];const d=th.dataset.d=th.dataset.d==='1'?'-1':'1';
rs.sort((a,b)=>(+a.cells[c].dataset.v-+b.cells[c].dataset.v)*-d);rs.forEach(r=>tb.appendChild(r))}});
</script>"""
    return page("全部演讲 · AIE Shanghai 2026", body, "talks")


def build_talk_page(t, a, enums, clean_md, raw_lines, promo, positions):
    lab = lambda k, c: short(enums[k].get(c, c or ""))
    _, blocks = parse_md(clean_md)
    paras = [b for b in blocks if b[0] == "p" and b[2]]
    cite = lambda item: evidence_link(item, paras)
    clean_h = render_transcript(clean_md, [order for order, _ in raw_lines])
    title = t["title"] if t["title"] and t["title"] != "Talk to be announced" else a["position"]
    parts = [f'<p class="crumb"><a href="../index.html">参会笔记</a><span>/</span><a href="../talks.html">全部演讲</a><span>/</span>{E(t["talk_id"])}</p>',
             f'<h1>{E(title)}</h1>',
             f'<p class="muted">{E(a.get("speakers") or t["speakers"])} · {E(a.get("org") or t["orgs"])} · {t["day"]} '
             f'{"主会场" if t["stage"] == "main" else "分会场"} · {t["actual_start"]}–{t["actual_end"]} · 场次 {E(t["talk_id"])}'
             f'{" · <span class=\"tag pr\">偏宣传</span>" if t["fid"] in promo else ""}</p>']
    if a:
        parts.append(f'<div class="core">{E(a.get("core_message", ""))}</div>')
        layer, group = positions[t["fid"]]
        kv = [("版图位置", f'{layer} · {group}'), ("细分", a.get("position", "")),
              ("讲者意图", lab("intent", a.get("intent"))), ("客户", lab("target_customer", a.get("target_customer"))),
              ("新信息量 / 推销浓度", f'{a.get("novelty", "")} / {a.get("pr_level", "")}')]
        parts.append('<dl class="kv">' + "".join(f"<dt>{k}</dt><dd>{E(str(v))}</dd>" for k, v in kv) + "</dl>")
        if a.get("skeleton"):
            parts.append("<h3>演讲提纲</h3><ol>" + "".join(f"<li>{E(x)}</li>" for x in a["skeleton"]) + "</ol>")
        if a.get("frameworks"):
            parts.append("<h3>讲者提出的框架</h3><ul>" + "".join(f"<li><b>{E(x['name'])}</b>：{E(x.get('gist', ''))}{cite(x)}</li>" for x in a["frameworks"]) + "</ul>")
        if a.get("offerings"):
            parts.append("<h3>产品与服务</h3><ul>" + "".join(f"<li><b>{E(o['name'])}</b>：{E(o.get('what', ''))}</li>" for o in a["offerings"]) + "</ul>")
        if a.get("non_consensus"):
            parts.append("<h3>非共识</h3><ul>" + "".join(f"<li>{E(x['point'])}<blockquote>{E(x['quote'])}{cite(x)}</blockquote></li>" for x in a["non_consensus"]) + "</ul>")
        if a.get("signals"):
            parts.append("<h3>信号</h3><ul>" + "".join(f"<li><span class=tag>{E(lab('signal_type', s.get('type')))}</span>{E(s['signal'])}{cite(s)}</li>" for s in a["signals"]) + "</ul>")
    parts.append('<h2>演讲转写</h2><p class="muted">根据现场语音识别整理，修正了专有名词，删去了口头语。〔?〕表示仍有疑问，数字尚未核实。</p>' + clean_h)
    raw = "".join(f'<div id="raw-{o}"><span class="o">{o}</span>{E(x)}</div>' for o, x in raw_lines)
    parts.append(f'<details><summary>原始识别文本（{len(raw_lines)} 行）</summary><div class="raw">{raw}</div></details>')
    parts.append('''<script>
function revealRaw(){const node=document.getElementById(location.hash.slice(1));if(!node)return;
const details=node.closest('details');if(details){details.open=true;node.scrollIntoView();}}
window.addEventListener('hashchange',revealRaw);revealRaw();
</script>''')
    return page(f'{title} · AIE Shanghai 2026', "".join(parts), "talks", depth=1)


def main(root, out):
    root = Path(root).resolve()
    if Path(out).is_symlink():
        raise ValueError("输出目录不能是符号链接")
    out = Path(out).resolve()
    protected = [root / name for name in ("data", "pipeline", ".git", "tests", ".github")]
    if root.is_relative_to(out) or any(out.is_relative_to(path) for path in protected):
        raise ValueError(f"输出目录不能覆盖源文件: {out}")
    require_valid(root)
    enums = json.loads((root / "pipeline/schemas/talk_analysis_v3.json").read_text(encoding="utf-8"))["enums"]
    talks = read_csv(root / "data/01_talks.csv")
    for t in talks:
        t["fid"] = fid_of(t["talk_id"])
    analyses = {}
    for t in talks:
        p = root / f"data/04_analysis_v3/{t['fid']}.json"
        analyses[t["fid"]] = json.loads(p.read_text(encoding="utf-8"))
    landscape = load_landscape(root)
    positions = talk_positions(landscape)
    clean_by_id = {t["fid"]: (root / f"data/03_clean/{t['fid']}.md").read_text(encoding="utf-8") for t in talks}
    paras_by_id = {fid: [b for b in parse_md(text)[1] if b[0] == "p" and b[2]] for fid, text in clean_by_id.items()}
    promo = {r["file_id"] for r in read_csv(root / "data/05_synthesis/substance_filter.csv")}
    segs = {r["seg_id"]: r for r in read_jsonl(root / "data/00_segments.jsonl")}
    by_talk = {}
    for r in read_jsonl(root / "data/01_segment_labels.jsonl"):
        if r["type"] == "talk" and r["session_id"]:
            by_talk.setdefault(fid_of(r["session_id"]), []).append((r["order"], segs[r["seg_id"]]["source_text"]))

    # Render everything and check every local link before replacing the previous site.
    rendered = {"index.html": build_report(root),
                "talks.html": build_talk_list(talks, analyses, enums, promo, positions, paras_by_id)}
    for t in talks:
        fid = t["fid"]
        rendered[f"talks/{fid}.html"] = build_talk_page(
            t, analyses[fid], enums, clean_by_id[fid], sorted(by_talk[fid]), promo, positions)
    out.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".aie-build-", dir=out.parent) as work:
        stage, backup = Path(work) / "site", Path(work) / "previous"
        if out.exists():
            shutil.copytree(out, stage)
        (stage / "talks").mkdir(parents=True, exist_ok=True)
        # talks/ is generated; discard pages for sessions removed from the inputs.
        for path in (stage / "talks").glob("*.html"):
            path.unlink()
        for name, content in rendered.items():
            (stage / name).write_text(content, encoding="utf-8")
        (stage / ".nojekyll").write_text("", encoding="utf-8")
        issues = check_site(stage)
        if issues:
            raise ValueError("站点检查失败:\n" + "\n".join(issues))
        if out.exists():
            out.rename(backup)
        try:
            stage.rename(out)
        except BaseException:
            if backup.exists():
                backup.rename(out)
            raise
    print("built", len(talks), "talk pages ->", out)


if __name__ == "__main__":
    try:
        main(*sys.argv[1:])
    except (OSError, ValueError) as error:
        raise SystemExit(str(error))
