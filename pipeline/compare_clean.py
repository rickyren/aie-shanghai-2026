"""Compare two proofreading runs of the same talks (e.g. Opus vs Sonnet) side by side.

Usage: python3 -I pipeline/compare_clean.py <project_root> <out_html> <dirA>=<labelA> <dirB>=<labelB> <file_id> [...]
dirs are relative to the project root and hold <file_id>.md / <file_id>.notes.json.
"""
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from review_clean import md_inline, parse_md  # noqa: E402


def load(root, d, fid, raw):
    md = (root / d / f"{fid}.md").read_text(encoding="utf-8")
    notes = json.loads((root / d / f"{fid}.notes.json").read_text(encoding="utf-8"))
    fm, blocks = parse_md(md)
    paras = [b for b in blocks if b[0] == "p"]
    covered = {o for _, _, r in paras if r for o in raw if r[0] <= o <= r[1]}
    q = md.count("〔?〕") + len(re.findall(r"〔(无法辨识|unintelligible)〕", md))
    ver = notes.get("verified", [])
    return {"fm": fm, "paras": paras, "notes": notes,
            "ratio": sum(len(b[1]) for b in blocks) / sum(len(t) for t in raw.values()),
            "q": q, "uncovered": len(set(raw) - covered), "n_paras": len(paras),
            "verified": {(v.get("resolved_to") or "").strip() for v in ver if v.get("resolved_to")},
            "corr": {(c.get("to") or "").strip() for c in notes.get("corrections", [])},
            "speakers": [s.get("name", "") for s in notes.get("speakers", [])]}


def diff_list(a, b):
    only_a, only_b = sorted(a - b), sorted(b - a)
    fmt = lambda xs: "、".join(html.escape(x) for x in xs) or "—"
    return f"<tr><td>{len(a & b)}</td><td>{fmt(only_a)}</td><td>{fmt(only_b)}</td></tr>"


def section(root, fid, runs):
    raw = {}
    for line in (root / f"data/03_clean/_input/{fid}.txt").open(encoding="utf-8"):
        o, t = line.rstrip("\n").split("\t", 1)
        raw[int(o)] = t
    (la, a), (lb, b) = [(lab, load(root, d, fid, raw)) for d, lab in runs]
    metrics = "".join(
        f"<tr><th>{name}</th><td>{fa(a)}</td><td>{fa(b)}</td></tr>" for name, fa in [
            ("字符比", lambda x: f"{x['ratio']:.0%}"), ("段落", lambda x: x["n_paras"]), ("〔?〕存疑", lambda x: x["q"]),
            ("联网确认", lambda x: len(x["verified"])), ("纠错条目", lambda x: len(x["corr"])),
            ("未覆盖原文行", lambda x: x["uncovered"]), ("发言人", lambda x: html.escape("、".join(x["speakers"])))])
    rows = []
    for _, text_a, r in a["paras"]:
        if not r:
            continue
        left = "".join(f'<div class="raw"><span class="o">{o}</span>{html.escape(raw[o])}</div>'
                       for o in sorted(raw) if r[0] <= o <= r[1])
        overlap = [t for _, t, rb in b["paras"] if rb and rb[0] <= r[1] and rb[1] >= r[0]]
        rows.append(f'<tr><td class="l">{left}</td><td>{md_inline(text_a)}<div class="rng">seg {r[0]}–{r[1]}</div></td>'
                    f'<td>{"<hr>".join(md_inline(t) for t in overlap)}</td></tr>')
    return f"""<section id="{fid}"><h2>{fid} · {html.escape(a['fm'].get('speakers', ''))}</h2>
<table class="m"><tr><th></th><th>{la}</th><th>{lb}</th></tr>{metrics}</table>
<h4>纠错 / 查证差异（按“改成什么”比较）</h4>
<table class="m"><tr><th>项目</th><th>两边都有</th><th>只有 {la}</th><th>只有 {lb}</th></tr>
<tr><th colspan=4 style="text-align:left">纠错</th></tr>{diff_list(a['corr'], b['corr'])}
<tr><th colspan=4 style="text-align:left">联网确认</th></tr>{diff_list(a['verified'], b['verified'])}</table>
<details><summary>逐段对照（以 {la} 的分段为准，右栏是 {lb} 覆盖同一范围的段落）</summary>
<table class="cmp"><tr><th>原始识别</th><th>{la}</th><th>{lb}</th></tr>{''.join(rows)}</table></details></section>"""


def main(root, out_html, run_a, run_b, *fids):
    root = Path(root)
    runs = [tuple(x.split("=", 1)) for x in (run_a, run_b)]
    body = "".join(section(root, f, runs) for f in fids)
    page = f"""<!doctype html><html lang="zh"><meta charset="utf-8"><title>清稿模型对比</title>
<style>
body{{font:14px/1.6 -apple-system,"PingFang SC",sans-serif;margin:24px auto;max-width:1500px;padding:0 16px;color:#222}}
table.m{{border-collapse:collapse;margin:6px 0 12px}} .m td,.m th{{border:1px solid #eee;padding:4px 10px;vertical-align:top;text-align:left;font-size:13px;max-width:560px}}
table.cmp{{border-collapse:collapse;width:100%}} .cmp td,.cmp th{{border-bottom:1px solid #eee;padding:8px;vertical-align:top;text-align:left;width:33%}}
.cmp td.l{{background:#fafafa}} .raw{{font-size:12px;color:#666;line-height:1.45}} .o{{color:#aaa;display:inline-block;width:38px}}
.rng{{font-size:11px;color:#aaa}} mark.q{{background:#fde7e9;color:#b3261e}} section{{border-top:3px solid #4a6cf7;margin-top:30px}}
</style>
<h1>清稿模型对比：{runs[0][1]} vs {runs[1][1]}</h1>
<p><b>这页给谁看</b>：决定批量清稿用哪个模型。两边用的是同一份 prompt（含联网查证）、同一份输入。
先看指标和“纠错 / 查证差异”：只出现在一边的条目，就是另一边漏改或改法不同的地方。展开“逐段对照”可以看具体文字。</p>
{body}</html>"""
    Path(out_html).write_text(page, encoding="utf-8")
    print("wrote", out_html)


if __name__ == "__main__":
    main(*sys.argv[1:])
