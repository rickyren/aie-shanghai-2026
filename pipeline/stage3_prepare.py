"""Stage 3 prep: per-talk input files, metadata + glossary, and a filled-in proofreading prompt.

Usage: python3 -I pipeline/stage3_prepare.py <project_root> [talk_id ...]   (no ids = all talks)
Writes data/03_clean/_input/<file_id>.{txt,meta.json,prompt.md} (file_id = filesystem-safe talk_id)
"""
import csv
import json
import re
import sys
from pathlib import Path

INPUT_DIR = "data/03_clean/_input"
OUTPUT_DIR = "data/03_clean"
# Terms that appear across talks and are commonly misheard; agenda names/orgs are added automatically.
TERMS = [
    "Milvus", "Zilliz", "OpenClaw", "MiniMax", "StepFun 阶跃星辰", "Kimi", "Moonshot AI 月之暗面", "Claude Code",
    "Cursor", "Manus", "Codex", "harness", "agent", "RL", "MCP", "LanceDB", "Lance", "Jina AI", "Elastic", "TiDB",
    "PingCAP", "Daytona", "Exa", "Langfuse", "ClickHouse", "HeyGen", "World Labs", "Liquid AI", "LFM", "Tripo",
    "VAST", "Baseten", "Arena (LMArena)", "You.com", "Dify", "Harvey", "Agoda", "DataHub", "Optiver", "Techcombank",
    "Visa", "Instagram", "Meta", "AutoArk", "WaytoAGI 通往AGI之路", "Linkloud", "真格基金 ZhenFund", "线性资本 Linear Capital",
    "Anthropic", "OpenAI", "DeepSeek", "Qwen 通义千问", "Gemini", "GPT", "Hugging Face", "GitHub", "vLLM", "SGLang",
    "KV cache", "LLM gateway", "sandbox", "Kubernetes", "VLA", "world model", "embodied AI 具身智能", "OPC",
]


def file_id(talk_id):
    """Filesystem-safe stem: 'offagenda:AJ (WaytoAGI)' -> 'offagenda_AJ_WaytoAGI'."""
    return re.sub(r"[^A-Za-z0-9-]+", "_", talk_id).strip("_")


def main(root, ids):
    root = Path(root)
    segs = {}
    for line in (root / "data/00_segments.jsonl").open(encoding="utf-8"):
        r = json.loads(line)
        segs[r["seg_id"]] = r
    labels = [json.loads(line) for line in (root / "data/01_segment_labels.jsonl").open(encoding="utf-8")]
    talks = {t["talk_id"]: t for t in csv.DictReader((root / "data/01_talks.csv").open(encoding="utf-8"))}
    agenda = list(csv.DictReader((root / "data/agenda.csv").open(encoding="utf-8")))
    glossary = sorted({x.strip() for a in agenda for x in (a["speakers"] + ";" + a["orgs"]).split(";") if x.strip()}
                      | {a["moderator"] for a in agenda if a["moderator"]} | set(TERMS))
    template = (root / "pipeline/prompts/clean_llm.md").read_text(encoding="utf-8")
    out = root / INPUT_DIR
    out.mkdir(parents=True, exist_ok=True)
    for tid in ids or list(talks):
        t = talks[tid]
        lines = [l for l in labels if l["session_id"] == tid and l["type"] == "talk"]
        fid = file_id(tid)
        with (out / f"{fid}.txt").open("w", encoding="utf-8") as f:
            for l in lines:
                f.write(f'{l["order"]}\t{segs[l["seg_id"]]["source_text"]}\n')
        a = next((x for x in agenda if x["session_id"] == tid), {})
        meta = {"talk_id": tid, "file_id": fid, "title": t["title"], "speakers": t["speakers"], "orgs": t["orgs"], "format": t["format"],
                "moderator": a.get("moderator", ""), "day": t["day"], "stage": t["stage"],
                "topic_id": t["topic_id"], "glossary": glossary}
        (out / f"{fid}.meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
        prompt = (template.replace("{input_dir}", INPUT_DIR).replace("{output_dir}", OUTPUT_DIR)
                  .replace("{file_id}", fid).replace("{talk_id}", tid))
        (out / f"{fid}.prompt.md").write_text(prompt, encoding="utf-8")
        print(tid, len(lines), "lines", sum(len(segs[l["seg_id"]]["source_text"]) for l in lines), "chars")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
