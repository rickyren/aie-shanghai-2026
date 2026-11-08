"""Stage 2: collect speaker facts from the proofreading notes into data/02_speakers.csv.

Usage: python3 -I pipeline/stage2_speakers.py <project_root>
One row per (talk, person). Facts come only from what was said in the talk; names may be web-verified.
"""
import csv
import json
import re
import sys
from pathlib import Path


def main(root):
    root = Path(root)
    talks = list(csv.DictReader((root / "data/01_talks.csv").open(encoding="utf-8")))
    rows, missing = [], []
    for t in talks:
        fid = re.sub(r"[^A-Za-z0-9-]+", "_", t["talk_id"]).strip("_")
        f = root / f"data/03_clean/{fid}.notes.json"
        if not f.exists():
            missing.append(t["talk_id"])
            continue
        notes = json.loads(f.read_text(encoding="utf-8"))
        for s in notes.get("speakers", []):
            rows.append({
                "talk_id": t["talk_id"], "day": t["day"], "stage": t["stage"], "format": t["format"],
                "agenda_speakers": t["speakers"], "agenda_orgs": t["orgs"],
                "name": s.get("name", ""), "name_as_heard": "、".join(s.get("name_as_heard", [])),
                "org": s.get("org", ""), "role": s.get("role", ""), "background": s.get("background", ""),
                "evidence_orders": ",".join(map(str, s.get("evidence_orders", []))) if isinstance(s.get("evidence_orders"), list) else s.get("evidence_orders", ""),
            })
    with (root / "data/02_speakers.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} speaker rows from {len(talks) - len(missing)} talks; missing notes: {missing}")


if __name__ == "__main__":
    main(sys.argv[1])
