"""Stage 4 prep: fill the analysis prompt for each talk.

Usage: python3 -I pipeline/stage4_prepare.py <project_root> [file_id ...]   (no ids = all proofread talks)
Writes data/04_analysis/_input/<file_id>.prompt.md
"""
import sys
from pathlib import Path


def main(root, ids):
    root = Path(root)
    template = (root / "pipeline/prompts/analyze_llm.md").read_text(encoding="utf-8")
    out = root / "data/04_analysis/_input"
    out.mkdir(parents=True, exist_ok=True)
    ids = ids or sorted(p.stem for p in (root / "data/03_clean").glob("*.md"))
    for fid in ids:
        assert (root / f"data/03_clean/{fid}.md").exists(), fid
        (out / f"{fid}.prompt.md").write_text(template.replace("{file_id}", fid), encoding="utf-8")
    print(len(ids), "prompts")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
