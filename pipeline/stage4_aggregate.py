"""Stage 4 aggregate: one row per talk from data/04_analysis_v3/*.json -> data/04_talks_analysis.csv.

Usage: python3 -I pipeline/stage4_aggregate.py <project_root>
"""
import csv
import json
import re
import sys
from pathlib import Path


def main(root):
    root = Path(root)
    schema = json.loads((root / "pipeline/schemas/talk_analysis_v3.json").read_text(encoding="utf-8"))["enums"]
    talks = list(csv.DictReader((root / "data/01_talks.csv").open(encoding="utf-8")))
    rows, missing = [], []
    for t in talks:
        fid = re.sub(r"[^A-Za-z0-9-]+", "_", t["talk_id"]).strip("_")
        f = root / f"data/04_analysis_v3/{fid}.json"
        if not f.exists():
            missing.append(fid)
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        rows.append({
            "talk_id": t["talk_id"], "file_id": fid, "day": t["day"], "stage": t["stage"], "format": t["format"],
            "speakers": d.get("speakers", ""), "org": d.get("org", ""),
            "layer": d.get("value_chain_layer", ""), "layer_label": schema["value_chain_layer"].get(d.get("value_chain_layer"), ""),
            "position": d.get("position", ""), "target_customer": d.get("target_customer", ""), "intent": d.get("intent", ""),
            "core_message": d.get("core_message", ""),
            "offerings": "；".join(f'{o["name"]}（{o.get("what", "")}）' for o in d.get("offerings", [])),
            "why_needed": d.get("why_needed", ""),
            "frameworks": "；".join(f'{x["name"]}：{x.get("gist", "")}' for x in d.get("frameworks", [])),
            "trend_categories": "、".join(d.get("trend_categories", [])),
            "novelty": d.get("novelty"), "pr_level": d.get("pr_level"),
            "n_non_consensus": len(d.get("non_consensus", [])), "n_signals": len(d.get("signals", [])),
            "n_data_signals": sum(s.get("type") == "data_signal" for s in d.get("signals", [])),
            "content_industry_note": d.get("content_industry_note", ""),
        })
    with (root / "data/04_talks_analysis.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} talks -> data/04_talks_analysis.csv; missing: {missing}")


if __name__ == "__main__":
    main(sys.argv[1])
