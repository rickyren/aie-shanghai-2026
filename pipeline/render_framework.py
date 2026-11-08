"""Render data/05_synthesis/framework.md (+ org_calibration.csv) to a self-contained HTML page.
Talk citations like [d1m05] become links to the per-talk digest page.

Usage: .venv/bin/python -I pipeline/render_framework.py <project_root> <out_html> [<markdown_path>] [--no-calibration]
"""
import csv
import html
import re
import sys
from pathlib import Path

import markdown

CITE = re.compile(r"\[((?:d[12][mb]\d{2}|offagenda_[A-Za-z0-9_]+))\]")


def main(root, out_html, md_path="data/05_synthesis/framework.md", with_calibration=True):
    root = Path(root)
    md = (root / md_path).read_text(encoding="utf-8")
    talks = {re.sub(r"[^A-Za-z0-9-]+", "_", t["talk_id"]).strip("_"): t
             for t in csv.DictReader((root / "data/01_talks.csv").open(encoding="utf-8"))}

    def link(m):
        fid = m.group(1)
        t = talks.get(fid)
        tip = html.escape(f'{t["speakers"]} · {t["orgs"]} · {t["title"]}') if t else "未知场次"
        return f'<a class="cite" href="talks_digest.html#{fid}" title="{tip}">{fid}</a>'

    body = markdown.markdown(md, extensions=["tables", "fenced_code", "toc", "sane_lists"])
    body = CITE.sub(link, body)
    body = body.replace("（推断）", '<span class="infer">（推断）</span>')

    cal_path = root / "data/05_synthesis/org_calibration.csv"
    cal = ""
    if with_calibration and cal_path.exists():
        rows = list(csv.DictReader(cal_path.open(encoding="utf-8")))
        cols = ["org", "final_layer", "sub_position", "what_they_sell", "sells_to", "changed_from_first_pass", "reason"]
        names = ["机构", "层级（校准后）", "细分位置", "卖什么", "卖给谁", "是否改动", "理由"]
        cal = ("<details><summary>附表：机构归类校准（" + str(len(rows)) + " 家）</summary><table class=cal><tr>"
               + "".join(f"<th>{n}</th>" for n in names) + "</tr>"
               + "".join("<tr>" + "".join(f"<td>{html.escape(r.get(c, '') or '')}</td>" for c in cols) + "</tr>" for r in rows)
               + "</table></details>")
    page = f"""<!doctype html><html lang="zh"><meta charset="utf-8"><title>AIE Shanghai 2026 · 行业框架</title>
<style>
body{{font:15px/1.75 -apple-system,"PingFang SC",sans-serif;margin:32px auto;max-width:960px;padding:0 20px;color:#1f2328}}
h1{{font-size:22px;border-bottom:2px solid #2f5bd3;padding-bottom:4px;margin-top:40px}} h2{{font-size:18px;margin-top:28px}} h3{{font-size:16px}}
a.cite{{font-size:11px;background:#eef3ff;color:#2f5bd3;border-radius:4px;padding:0 4px;text-decoration:none;margin:0 1px}}
.infer{{color:#57606a;font-size:12px}} pre{{background:#f6f8fa;padding:12px;border-radius:8px;overflow-x:auto;font-size:13px;line-height:1.5}}
table{{border-collapse:collapse;font-size:13px;margin:10px 0}} td,th{{border:1px solid #e5e5e5;padding:5px 8px;vertical-align:top;text-align:left}}
blockquote{{border-left:3px solid #ddd;margin:8px 0;padding-left:12px;color:#555}} .meta{{color:#888;font-size:12px}}
</style>
{body}
{cal}
</html>"""
    Path(out_html).write_text(page, encoding="utf-8")
    print("wrote", out_html)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--no-calibration"]
    main(*args, with_calibration="--no-calibration" not in sys.argv)
