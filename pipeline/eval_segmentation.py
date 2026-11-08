"""Score segmentation outputs against gold spans and render a comparison page.

Usage: python3 -I pipeline/eval_segmentation.py <eval_dir> <out_html> <labels.json> [<labels.json> ...]
<eval_dir> holds gold.json and window.txt.
"""
import html
import json
import sys
from pathlib import Path

COLORS = {"talk": "#4a6cf7", "host": "#f2994a", "logistics": "#9aa0a6", "noise": "#d93025"}
SESSION_SHADES = ["#4a6cf7", "#22a06b", "#8e44ad", "#00a3bf", "#c0392b", "#b7950b"]


def expand(spans):
    out = {}
    for s in spans:
        for o in range(s["from"], s["to"] + 1):
            out[o] = (s["type"], s.get("session_id"))
    return out


def talk_ranges(lab):
    """session_id -> (first, last) order of its talk segments."""
    rng = {}
    for o, (t, sid) in sorted(lab.items()):
        if t == "talk" and sid:
            a, _ = rng.get(sid, (o, o))
            rng[sid] = (a, o)
    return rng


def score(gold, pred, ambiguous, orders):
    scored = [o for o in orders if o not in ambiguous]
    binary = sum((gold[o][0] == "talk") == (pred[o][0] == "talk") for o in scored)
    four = sum(gold[o][0] == pred[o][0] for o in scored)
    # talk segments: are they attributed to the right session?
    gold_talk = [o for o in scored if gold[o][0] == "talk"]
    sess = sum(pred[o] == gold[o] for o in gold_talk)
    leaked = [o for o in scored if gold[o][0] != "talk" and pred[o][0] == "talk"]
    lost = [o for o in scored if gold[o][0] == "talk" and pred[o][0] != "talk"]
    g_rng, p_rng = talk_ranges(gold), talk_ranges(pred)
    bounds = {sid: (p_rng[sid][0] - a, p_rng[sid][1] - b) if sid in p_rng else None
              for sid, (a, b) in g_rng.items()}
    extra = sorted(set(p_rng) - set(g_rng))
    return {"n": len(scored), "binary": binary, "four": four, "sess": sess, "n_talk": len(gold_talk),
            "leaked": leaked, "lost": lost, "bounds": bounds, "extra": extra}


def strip(lab, orders, by_session):
    cells = []
    sids = sorted({sid for _, sid in lab.values() if sid})
    for o in orders:
        t, sid = lab[o]
        c = SESSION_SHADES[sids.index(sid) % len(SESSION_SHADES)] if by_session and t == "talk" and sid else COLORS[t]
        cells.append(f'<i style="background:{c}" title="{o} {t} {sid or ""}"></i>')
    return "".join(cells)


def main(eval_dir, out_html, *label_files):
    eval_dir = Path(eval_dir)
    gold_doc = json.loads((eval_dir / "gold.json").read_text(encoding="utf-8"))
    gold = expand(gold_doc["spans"])
    ambiguous = set(gold_doc.get("ambiguous", []))
    text = {int(line.split("\t")[0]): line.rstrip("\n").split("\t", 2)[2]
            for line in (eval_dir / "window.txt").open(encoding="utf-8")}
    orders = sorted(gold)
    methods = []
    for f in label_files:
        doc = json.loads(Path(f).read_text(encoding="utf-8"))
        pred = expand(doc["spans"])
        missing = [o for o in orders if o not in pred]
        assert not missing, f"{f} misses {missing[:5]}"
        methods.append((doc["method"], doc, pred, score(gold, pred, ambiguous, orders)))

    def pct(a, b):
        return f"{a}/{b} ({a / b:.1%})"

    rows = []
    for name, doc, pred, s in methods:
        b = "<br>".join(f"{sid}: {'未识别' if v is None else f'起 {v[0]:+d} · 止 {v[1]:+d}'}"
                        for sid, v in s["bounds"].items())
        stats = doc.get("stats", {})
        cost = f"{stats.get('wall_s', '?')}s · {stats.get('input_tokens', '?'):,} tok" if stats else html.escape(doc.get("cost", "-"))
        rows.append(f"<tr><th>{name}</th><td>{pct(s['binary'], s['n'])}</td><td>{pct(s['four'], s['n'])}</td>"
                    f"<td>{pct(s['sess'], s['n_talk'])}</td><td>{len(s['leaked'])}</td><td>{len(s['lost'])}</td>"
                    f"<td class=small>{b}{'<br>多出: ' + ', '.join(s['extra']) if s['extra'] else ''}</td><td class=small>{cost}</td></tr>")

    strips = [f'<div class="lbl">gold</div><div class="strip">{strip(gold, orders, False)}</div>'
              f'<div class="strip">{strip(gold, orders, True)}</div>']
    for name, _, pred, _ in methods:
        strips.append(f'<div class="lbl">{name}</div><div class="strip">{strip(pred, orders, False)}</div>'
                      f'<div class="strip">{strip(pred, orders, True)}</div>')

    diff_rows = []
    for o in orders:
        labs = [pred[o] for _, _, pred, _ in methods]
        if all(l == gold[o] for l in labs):
            continue
        cells = "".join(f'<td class="{"ok" if l == gold[o] else ("amb" if o in ambiguous else "no")}">{l[0]} {l[1] or ""}</td>'
                        for l in labs)
        diff_rows.append(f"<tr><td>{o}{' <span class=tag>ambiguous</span>' if o in ambiguous else ''}</td>"
                         f"<td>{html.escape(text[o][:120])}</td><td>{gold[o][0]} {gold[o][1] or ''}</td>{cells}</tr>")

    legend = "".join(f'<span><i style="background:{c}"></i>{t}</span>' for t, c in COLORS.items())
    mnames = "".join(f"<th>{m[0]}</th>" for m in methods)
    page = f"""<!doctype html><html lang="zh"><meta charset="utf-8"><title>切分实测 · 1 小时窗口</title>
<style>
body{{font:14px/1.5 -apple-system,"PingFang SC",sans-serif;margin:24px;color:#222;max-width:1200px}}
table{{border-collapse:collapse;width:100%;margin:8px 0 20px}} td,th{{border-bottom:1px solid #e5e5e5;padding:6px 8px;text-align:left;vertical-align:top}}
.small{{font-size:12px}} .strip{{display:flex;height:14px;margin:2px 0}} .strip i{{flex:1;min-width:0}}
.lbl{{font-size:12px;color:#555;margin-top:10px}} .legend span{{margin-right:14px;font-size:12px}} .legend i{{display:inline-block;width:10px;height:10px;margin-right:4px}}
.ok{{color:#137333}} .no{{color:#c5221f;font-weight:600}} .amb{{color:#b26a00}} .tag{{font-size:11px;background:#fff1d6;border-radius:4px;padding:0 4px}}
</style>
<h1>切分实测：Jev 打标 + 规则 vs LLM 子 agent</h1>
<p>窗口：{gold_doc['window']['topic_id']}:{orders[0]}–{orders[-1]}（11/5 主会场 15:27–16:42，{len(orders)} 段）。
里面有 Manus 的结尾、茶歇（含台上调试闲聊）、Exa / Zilliz / Optiver 三场完整演讲，以及 TiDB 的开头。
金标由人工逐段核对确定。{len(ambiguous)} 段边界上有歧义，判 talk 或非 talk 都算对，不计入准确率。</p>
<h3>指标</h3>
<table><tr><th>方法</th><th>talk/非 talk 准确率</th><th>四分类准确率</th><th>talk 段归属到正确场次</th><th>非 talk 混进正文</th><th>正文被误删</th><th>每场起止误差（段）</th><th>耗时 · token</th></tr>
{''.join(rows)}</table>
<h3>时间线</h3><div class="legend">{legend} · 每个方法第二条按场次着色</div>
{''.join(strips)}
<h3>与金标不一致的段（{len(diff_rows)}）</h3>
<table><tr><th>order</th><th>原文</th><th>金标</th>{mnames}</tr>{''.join(diff_rows) or '<tr><td colspan=9>无</td></tr>'}</table>
</html>"""
    Path(out_html).write_text(page, encoding="utf-8")
    for name, _, _, s in methods:
        print(name, "binary", pct(s["binary"], s["n"]), "4cls", pct(s["four"], s["n"]), "sess", pct(s["sess"], s["n_talk"]),
              "leaked", s["leaked"], "lost", s["lost"], "bounds", s["bounds"], "extra", s["extra"])


if __name__ == "__main__":
    main(*sys.argv[1:])
