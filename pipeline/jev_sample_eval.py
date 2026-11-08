"""Run TypeSafe Jev on the hand-labelled sample set and render a review table.

Usage: .venv/bin/python -I pipeline/jev_sample_eval.py <project_root>
Key: TYPESAFE_API_KEY env var, or macOS Keychain item with service name TYPESAFE_API_KEY.
"""
import asyncio
import csv
import html
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from jev_common import CONTEXT, TYPES, api_key, classify  # noqa: E402


def render(results, dest):
    ok = [r for r in results if "error" not in r]
    def acc(rows):
        return f"{sum(r['pred_type'] == r['gold_type'] for r in rows)}/{len(rows)}" if rows else "-"
    by_diff = {d: [r for r in ok if r["difficulty"] == d] for d in ("easy", "hard", "mixed")}
    conf = Counter((r["gold_type"], r["pred_type"]) for r in ok)
    tp = sum(r["start_p"] >= .5 and r["gold_start"] == 1 for r in ok)
    fp = sum(r["start_p"] >= .5 and r["gold_start"] == 0 for r in ok)
    fn = sum(r["start_p"] < .5 and r["gold_start"] == 1 for r in ok)
    lat = sorted(r["latency_ms"] for r in ok)
    tok = sum(r["in_tok"] for r in ok)

    def bar(p):
        return f'<span class="bar"><i style="width:{p*100:.0f}%"></i></span>{p:.2f}'

    rows_html = []
    order = sorted(results, key=lambda r: ("error" not in r and r["pred_type"] == r["gold_type"]
                                           and (r["start_p"] >= .5) == bool(r["gold_start"]), r["seg_id"]))
    for r in order:
        st = r["state"]
        ctx = "".join(f'<div class="ctx">{html.escape(t)}</div>' for t in st["before"]) + \
              f'<div class="tgt">{html.escape(st["target"] or "")}</div>' + \
              "".join(f'<div class="ctx">{html.escape(t)}</div>' for t in st["after"])
        if "error" in r:
            pred = f'<td colspan="4" class="err">{html.escape(r["error"])}</td>'
            cls = "bad"
        else:
            type_ok = r["pred_type"] == r["gold_type"]
            start_ok = (r["start_p"] >= .5) == bool(r["gold_start"])
            cls = "" if type_ok and start_ok else "bad"
            probs = "<br>".join(f"{k} {bar(r['probs'].get(k, 0))}" for k in TYPES)
            pred = (f'<td class="{"ok" if type_ok else "no"}"><b>{r["pred_type"]}</b> ({r["confidence"]:.2f})</td>'
                    f'<td class="probs">{probs}</td>'
                    f'<td class="{"ok" if start_ok else "no"}">{bar(r["start_p"])}</td>'
                    f'<td>{r["latency_ms"]}ms</td>')
        rows_html.append(
            f'<tr class="{cls} d-{r["difficulty"]}"><td><code>{r["seg_id"]}</code><br>'
            f'<span class="tag">{r["difficulty"]}</span></td>'
            f'<td><details><summary>{html.escape((st["target"] or "")[:80])}</summary>{ctx}</details>'
            f'<div class="note">{html.escape(r["note"])}</div></td>'
            f'<td><b>{r["gold_type"]}</b>{" · start" if r["gold_start"] else ""}</td>{pred}</tr>')

    types_present = [t for t in TYPES if any(t in k for k in conf)]
    cm = "<tr><th>gold ↓ / pred →</th>" + "".join(f"<th>{t}</th>" for t in types_present) + "</tr>" + "".join(
        f"<tr><th>{g}</th>" + "".join(f"<td>{conf.get((g, p), 0) or ''}</td>" for p in types_present) + "</tr>"
        for g in types_present)
    model = ok[0]["model"] if ok else "?"
    page = f"""<!doctype html><html lang="zh"><meta charset="utf-8"><title>Jev 样本评测</title>
<style>
body{{font:14px/1.5 -apple-system,"PingFang SC",sans-serif;margin:24px;color:#222}}
h1{{font-size:20px}} table{{border-collapse:collapse;width:100%}} td,th{{border-bottom:1px solid #e5e5e5;padding:6px 8px;vertical-align:top;text-align:left}}
.kpi{{display:flex;gap:24px;margin:12px 0}} .kpi div{{background:#f5f5f7;padding:10px 14px;border-radius:8px}} .kpi b{{font-size:18px;display:block}}
tr.bad{{background:#fff4f2}} .ok{{color:#137333}} .no{{color:#c5221f}} .err{{color:#c5221f}}
.ctx{{color:#888;font-size:12px}} .tgt{{background:#fff3c4;padding:2px 4px;margin:2px 0}} .note{{color:#666;font-size:12px}}
.tag{{font-size:11px;background:#eee;border-radius:4px;padding:0 4px}} .probs{{font-size:12px;white-space:nowrap}}
.bar{{display:inline-block;width:60px;height:6px;background:#eee;margin:0 4px;vertical-align:middle}} .bar i{{display:block;height:100%;background:#4a6cf7}}
table.cm{{width:auto}} .filters label{{margin-right:12px}}
</style>
<h1>TypeSafe Jev · 切分样本评测</h1>
<p>{len(results)} 条人工金标样本，每条带前后各 {CONTEXT} 段上下文。模型 <code>{model}</code>。分类错误或起点判断错误的行排在最前面，标为浅红色。点击文本可以展开上下文。</p>
<div class="kpi">
<div>分类准确率 · 全部<b>{acc(ok)}</b></div><div>easy<b>{acc(by_diff['easy'])}</b></div>
<div>hard<b>{acc(by_diff['hard'])}</b></div><div>mixed<b>{acc(by_diff['mixed'])}</b></div>
<div>talk_start @0.5<b>P {tp}/{tp+fp} · R {tp}/{tp+fn}</b></div>
<div>延迟 p50 / max<b>{lat[len(lat)//2] if lat else '-'} / {lat[-1] if lat else '-'} ms</b></div>
<div>输入 token<b>{tok:,}</b></div><div>报错<b>{len(results)-len(ok)}</b></div>
</div>
<h3>混淆矩阵（segment_type）</h3><table class="cm">{cm}</table>
<h3>明细</h3>
<div class="filters"><label><input type="checkbox" id="onlybad"> 只看错误</label></div>
<table id="t"><tr><th>seg</th><th>目标段（展开看上下文）</th><th>金标</th><th>Jev 分类</th><th>类别概率</th><th>talk_start</th><th>延迟</th></tr>
{''.join(rows_html)}</table>
<script>document.getElementById('onlybad').onchange=e=>document.querySelectorAll('#t tr:not(:first-child)').forEach(r=>r.style.display=e.target.checked&&!r.classList.contains('bad')?'none':'')</script>
</html>"""
    dest.write_text(page, encoding="utf-8")


def main(root):
    root = Path(root)
    segs = {}
    for line in (root / "data/00_segments.jsonl").open(encoding="utf-8"):
        r = json.loads(line)
        segs[r["seg_id"]] = r
    with (root / "data/samples/jev_gold.csv").open(encoding="utf-8") as f:
        samples = [{**r, "gold_start": int(r["gold_start"])} for r in csv.DictReader(f)]
    missing = [s["seg_id"] for s in samples if s["seg_id"] not in segs]
    assert not missing, missing
    results = asyncio.run(classify(samples, segs, api_key()))
    with (root / "data/samples/jev_results.jsonl").open("w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    dest = root / "out/jev_sample_review.html"
    render(results, dest)
    ok = [r for r in results if "error" not in r]
    print(f"{len(ok)}/{len(results)} ok, type acc {sum(r['pred_type'] == r['gold_type'] for r in ok)}/{len(ok)} -> {dest}")
    for r in results:
        if "error" in r:
            print("ERR", r["seg_id"], r["error"][:200])
            break


if __name__ == "__main__":
    main(sys.argv[1])
