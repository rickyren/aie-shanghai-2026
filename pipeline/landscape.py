"""Load and validate the report’s editorial company classifications."""
import json
from pathlib import Path


def load_landscape(root):
    data = json.loads((Path(root) / "data/05_synthesis/landscape.json").read_text(encoding="utf-8"))
    talk_positions(data)  # validate before rendering
    return data


def talk_positions(data):
    positions = {}
    layers = set()
    for layer in data["layers"]:
        if layer["name"] in layers:
            raise ValueError(f"重复版图层级: {layer['name']}")
        layers.add(layer["name"])
        for row_index, row in enumerate(layer["rows"]):
            weights = layer.get("widths", [[1] * len(r) for r in layer["rows"]])[row_index]
            if len(weights) != len(row) or any(w <= 0 for w in weights):
                raise ValueError(f"{layer['name']}: 版图列宽配置无效")
            for group in row:
                if not group["entities"]:
                    raise ValueError(f"{group['name']}: 空版图分组")
                for entity in group["entities"]:
                    if not entity["name"].strip():
                        raise ValueError("版图实体名称不能为空")
                    for fid in entity.get("talk_ids", []):
                        if fid in positions:
                            raise ValueError(f"重复的版图主分类: {fid}")
                        if entity.get("exhibitor"):
                            raise ValueError(f"展商不能同时是演讲场次: {fid}")
                        positions[fid] = (layer["name"], group["name"])
    return positions
