"""Validate V3 structure and its evidence against the cited transcript paragraphs."""
import re

from jsonschema import Draft202012Validator

NORM = re.compile(r"[\s*`\"“”'‘’「」『』]+")


def norm(text):
    return NORM.sub("", text or "")


def seg_range(value):
    match = re.fullmatch(r"\s*(\d+)\s*(?:[–-]\s*(\d+))?\s*", str(value or ""))
    return (int(match[1]), int(match[2] or match[1])) if match else None


def validate(doc, schema, paras):
    issues = []
    for error in Draft202012Validator(schema).iter_errors(doc):
        path = ".".join(map(str, error.absolute_path)) or "analysis"
        issues.append(f"{path}: {error.message}")
    # Do not inspect nested values until their types and required fields are valid.
    if issues:
        return issues
    if not paras:
        return ["清稿缺少带 seg 编号的段落"]
    ranges = [r for _, _, r in paras]
    for field in ("non_consensus", "signals", "frameworks"):
        for index, item in enumerate(doc[field]):
            where = f"{field}[{index}]"
            span = seg_range(item["seg"])
            if not span or span[0] > span[1]:
                issues.append(f"{where}: seg 区间无效或倒序: {item['seg']!r}")
                continue
            if not any(a <= span[0] <= b for a, b in ranges) or not any(a <= span[1] <= b for a, b in ranges):
                issues.append(f"{where}: seg {item['seg']} 不在清稿段落范围内")
                continue
            if field == "non_consensus":
                cited = "".join(text for _, text, (a, b) in paras if a <= span[1] and b >= span[0])
                quote = norm(item["quote"])
                if not quote or quote not in norm(cited):
                    issues.append(f"{where}: 引用在所标注的 seg {item['seg']} 段落中找不到")
    return issues
