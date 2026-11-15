"""Stage 4 prep: fill the analysis prompt for each talk.

Usage: python3 -I pipeline/stage4_prepare.py <project_root> [file_id ...]   (no ids = all proofread talks)
Writes data/04_analysis_v3/_input/<file_id>.prompt.md (V3 is the current analysis format).
"""
import sys
from pathlib import Path


def main(root, ids):
    root = Path(root)
    template = (root / "pipeline/prompts/analyze_llm_v3.md").read_text(encoding="utf-8")
    out = root / "data/04_analysis_v3/_input"
    out.mkdir(parents=True, exist_ok=True)
    ids = ids or sorted(p.stem for p in (root / "data/03_clean").glob("*.md"))
    for fid in ids:
        for suffix in ("md", "notes.json", "_input_meta"):
            path = (root / f"data/03_clean/_input/{fid}.meta.json" if suffix == "_input_meta"
                    else root / f"data/03_clean/{fid}.{suffix}")
            if not path.is_file():
                raise SystemExit(f"Missing {path}. Run stage3_prepare.py first to prepare transcript inputs.")
        prompt = template.replace("{file_id}", fid).replace("<project_root>", str(root.resolve()))
        (out / f"{fid}.prompt.md").write_text(prompt, encoding="utf-8")
    print(len(ids), "prompts")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
