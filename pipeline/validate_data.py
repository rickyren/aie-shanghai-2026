"""Check the inputs used by the site without changing them or calling an API.

Usage: python pipeline/validate_data.py <project_root> [--talk <file_id>]
"""
import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analysis_validation import validate
from review_clean import parse_md


def file_id(talk_id):
    return re.sub(r"[^A-Za-z0-9-]+", "_", talk_id).strip("_")


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def duplicates(values):
    return sorted(str(value) for value, count in Counter(values).items() if count > 1)


def validate_inputs(root, only=None):
    root = Path(root)
    issues = []
    try:
        schema = json.loads((root / "pipeline/schemas/talk_analysis_v3.json").read_text(encoding="utf-8"))
        talks = read_csv(root / "data/01_talks.csv")
        segments = read_jsonl(root / "data/00_segments.jsonl")
        labels = read_jsonl(root / "data/01_segment_labels.jsonl")
    except (OSError, ValueError) as error:
        return [str(error)]
    if not talks or not segments or not labels:
        return ["场次、转写和标签文件均不能为空"]
    for name, values in (("talk_id", [t["talk_id"] for t in talks]),
                         ("file_id", [file_id(t["talk_id"]) for t in talks]),
                         ("segment", [s["seg_id"] for s in segments]),
                         ("label", [s["seg_id"] for s in labels])):
        repeated = duplicates(values)
        if repeated:
            issues.append(f"重复 {name}: {', '.join(repeated)}")
    by_id = {s["seg_id"]: s for s in segments}
    label_ids = {r["seg_id"] for r in labels}
    if set(by_id) != label_ids:
        issues.append(f"转写与标签不对应: 缺少 {len(set(by_id) - label_ids)}，多出 {len(label_ids - set(by_id))}")
    talk_map = {t["talk_id"]: t for t in talks}
    by_talk = defaultdict(list)
    for row in labels:
        sid = row["seg_id"]
        segment = by_id.get(sid)
        if not segment:
            continue
        if sid != f"{segment['topic_id']}:{segment['order']}" or any(row[k] != segment[k] for k in ("topic_id", "order")):
            issues.append(f"{sid}: topic/order 不一致")
        if row["type"] not in {"talk", "host", "logistics", "noise"}:
            issues.append(f"{sid}: 标签类型无效: {row['type']!r}")
        if row["type"] == "talk":
            tid = row.get("session_id")
            if tid not in talk_map:
                issues.append(f"{sid}: 场次不存在: {tid!r}")
            else:
                by_talk[tid].append(row)
                if str(row["topic_id"]) != talk_map[tid]["topic_id"]:
                    issues.append(f"{sid}: 不属于场次 {tid} 的 topic")
        elif row.get("session_id"):
            issues.append(f"{sid}: 非演讲段不应指定场次")
    expected = {file_id(t["talk_id"]) for t in talks}
    if only and only not in expected:
        issues.append(f"未知场次: {only}")
    if not only:
        for folder, pattern, suffix in (("04_analysis_v3", "*.json", ".json"),
                                        ("03_clean", "*.md", ".md"),
                                        ("03_clean", "*.notes.json", ".notes.json")):
            found = {p.name.removesuffix(suffix) for p in (root / "data" / folder).glob(pattern)}
            for fid in sorted(found - expected):
                issues.append(f"data/{folder}: 孤立文件 {fid}{suffix}")
    for talk in talks:
        fid, tid = file_id(talk["talk_id"]), talk["talk_id"]
        if only and fid != only:
            continue
        rows = by_talk[tid]
        if not rows:
            issues.append(f"{fid}: 没有演讲原文")
        elif (len(rows) != int(talk["n_talk_segs"]) or min(r["order"] for r in rows) != int(talk["seg_start"])
              or max(r["order"] for r in rows) != int(talk["seg_end"])):
            issues.append(f"{fid}: 场次表中的段数或起止位置与标签不符")
        try:
            doc = json.loads((root / f"data/04_analysis_v3/{fid}.json").read_text(encoding="utf-8"))
            clean = (root / f"data/03_clean/{fid}.md").read_text(encoding="utf-8")
            notes = json.loads((root / f"data/03_clean/{fid}.notes.json").read_text(encoding="utf-8"))
            front, blocks = parse_md(clean)
        except (OSError, ValueError) as error:
            issues.append(f"{fid}: {error}")
            continue
        if not isinstance(doc, dict) or not isinstance(notes, dict):
            issues.append(f"{fid}: 分析和校对记录必须是 JSON 对象")
            continue
        if doc.get("talk_id") != tid or front.get("talk_id") != tid or notes.get("talk_id") != tid:
            issues.append(f"{fid}: 分析、清稿或校对记录的 talk_id 与场次表不符")
        paras = [b for b in blocks if b[0] == "p" and b[2]]
        analysis_issues = validate(doc, schema, paras)
        issues.extend(f"{fid}: {message}" for message in analysis_issues)
        if not analysis_issues and (talk["format"] == "panel" or len(notes.get("speakers", [])) > 1):
            for index, item in enumerate(doc.get("non_consensus", [])):
                if isinstance(item, dict) and not str(item.get("speaker", "")).strip():
                    issues.append(f"{fid}: non_consensus[{index}] 多人演讲需标明讲者")
        if any(b[0] == "p" and not b[2] for b in blocks):
            issues.append(f"{fid}: 清稿有缺少 seg 的段落")
        previous = None
        for _, _, (a, b) in paras:
            if a > b or (previous and a < previous[0]):
                issues.append(f"{fid}: 清稿 seg 倒序: {a}–{b}")
            if rows and (a < int(talk["seg_start"]) or b > int(talk["seg_end"])):
                issues.append(f"{fid}: 清稿 seg {a}–{b} 超出本场原文")
            previous = (a, b)
    if not only:
        try:
            promo = read_csv(root / "data/05_synthesis/substance_filter.csv")
            for item in promo:
                if item["file_id"] not in expected:
                    issues.append(f"偏宣传名单包含未知场次: {item['file_id']}")
            from landscape import load_landscape, talk_positions
            landscape = load_landscape(root)
            positions = talk_positions(landscape)
            if set(positions) != expected:
                issues.append(f"版图场次不对应: 缺少 {sorted(expected - set(positions))}，多出 {sorted(set(positions) - expected)}")
            for layer in landscape["layers"]:
                for row in layer["rows"]:
                    for group in row:
                        for entity in group["entities"]:
                            for fid in entity.get("related_talk_ids", []):
                                if fid not in expected:
                                    issues.append(f"版图关联了未知场次: {fid}")
        except (OSError, ValueError) as error:
            issues.append(str(error))
    return issues


def require_valid(root):
    issues = validate_inputs(root)
    if issues:
        raise ValueError("输入校验失败:\n" + "\n".join(f"- {issue}" for issue in issues))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--talk", help="Validate one analysis while it is being edited")
    args = parser.parse_args()
    issues = validate_inputs(args.root, args.talk)
    for issue in issues:
        print(issue)
    if issues:
        raise SystemExit(1)
    print("数据校验通过" + (f": {args.talk}" if args.talk else ""))


if __name__ == "__main__":
    main()
