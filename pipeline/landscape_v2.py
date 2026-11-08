"""Industry landscape as an editorial market map: layer labels on the left, groups as columns,
one rounded tag per company. Black/grey ink, one blue for structure labels; exhibitors get a dashed grey tag.

Usage: python3 -I pipeline/landscape_v2.py <out.svg>
Entity syntax: "Name|descriptor"; a trailing "*" marks an expo exhibitor.
"""
import sys

FONT = "-apple-system,'PingFang SC','Helvetica Neue',sans-serif"
INK, SUB, MUTED, EXH = "#1f2328", "#57606a", "#6e7781", "#8c959f"
BLUE, RULE, TAG_FILL = "#2f5bd3", "#e4e7eb", "#f1f4f9"

W = 1000
LABEL_X, CONTENT_X, CONTENT_R = 0, 150, 1000
COL_GAP, TAG_GAP_X, TAG_GAP_Y = 32, 8, 8
TAG_H, TAG_PAD = 28, 11
NAME_SIZE, DESC_SIZE = 13, 11.5


def text_w(s, size):
    """Rough rendered width in px for PingFang / SF at `size`."""
    w = 0.0
    for ch in s:
        if "一" <= ch <= "鿿" or ch in "：、（）":
            w += 1.0
        elif ch in " .,'·":
            w += 0.32
        elif ch in "iljftrI1|":
            w += 0.32
        elif ch in "→":
            w += 1.0
        elif ch.isupper() or ch in "mwMW":
            w += 0.68
        elif ch.isdigit():
            w += 0.6
        else:
            w += 0.56
    return w * size


def tag_size(entity):
    exh = entity.endswith("*")
    name, _, desc = entity.rstrip("*").partition("|")
    w = TAG_PAD * 2 + text_w(name, NAME_SIZE) * 1.04 + (6 + text_w(desc, DESC_SIZE) * 1.04 if desc else 0)
    return w, name, desc, exh


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def tag(x, y, entity):
    w, name, desc, exh = tag_size(entity)
    if exh:
        rect = f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{TAG_H}" rx="6" fill="#fff" stroke="#c9cfd6" stroke-dasharray="3 2.5"/>'
        name_c, desc_c = EXH, EXH
    else:
        rect = f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{TAG_H}" rx="6" fill="{TAG_FILL}"/>'
        name_c, desc_c = INK, MUTED
    base = y + TAG_H / 2 + 4.5
    # name and descriptor share one <text>, so the browser places the descriptor right after the name
    desc_svg = f'<tspan dx="6" font-size="{DESC_SIZE}" font-weight="400" fill="{desc_c}">{esc(desc)}</tspan>' if desc else ""
    out = [rect, f'<text x="{x + TAG_PAD:.1f}" y="{base:.1f}" font-size="{NAME_SIZE}" fill="{name_c}" font-weight="500">{esc(name)}{desc_svg}</text>']
    return out, w


def layout_group(x, y, width, title, entities):
    """Title + tags flowing left to right, wrapping inside `width`. Returns (svg, height)."""
    out = [f'<text x="{x}" y="{y + 13}" font-size="13" font-weight="600" fill="{INK}">{esc(title)}</text>']
    cx, cy = x, y + 24
    for e in entities:
        w = tag_size(e)[0]
        if cx > x and cx + w > x + width:
            cx, cy = x, cy + TAG_H + TAG_GAP_Y
        svg, w = tag(cx, cy, e)
        out += svg
        cx += w + TAG_GAP_X
    return out, (cy + TAG_H) - y


GRID_COLS, GRID_GAP = 12, 24
UNIT = (CONTENT_R - CONTENT_X - GRID_GAP * (GRID_COLS - 1)) / GRID_COLS


def col_x(c):
    return CONTENT_X + c * (UNIT + GRID_GAP)


def span_w(n):
    return n * UNIT + (n - 1) * GRID_GAP


def row(y, groups):
    """groups: (start_col, span, title, entities) on a shared 12-column grid."""
    out, h = [], 0
    for start, span, title, ents in groups:
        svg, gh = layout_group(col_x(start), y, span_w(span), title, ents)
        out += svg
        h = max(h, gh)
    return out, h


def landscape():
    o = []
    y = 8

    def layer(label, groups, sub=None, rule=True, label_on=True):
        nonlocal y
        if rule:
            o.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{RULE}"/>')
            y += 22
        if label_on:
            o.append(f'<text x="{LABEL_X}" y="{y + 13}" font-size="15" font-weight="700" fill="{BLUE}">{esc(label)}</text>')
        if sub:
            o.append(f'<text x="{LABEL_X + 12}" y="{y + (38 if label_on else 13)}" font-size="12.5" fill="{SUB}">{esc(sub)}</text>')
        svg, h = row(y, groups)
        o.extend(svg)
        y += max(h, 44 if label_on and sub else 20) + 22

    layer("应用", [
        (0, 2, "通用 / 个人 agent", ["Manus", "OpenClaw", "YouMind"]),
        (2, 6, "垂直行业", ["Harvey|法律", "AhaCreator|达人营销", "Cookiy|用户研究", "HeyGen|视频", "CHILING|美妆", "KouShi|语言学习", "HellYeah|广告投放*"]),
        (8, 4, "企业内部落地", ["Optiver|交易", "Techcombank|银行", "Agoda|旅游", "Instagram|社交", "HICAP|制造", "Data4Life|医疗"]),
    ], rule=False)

    infra_top = y
    layer("Agent Infra", [
        (0, 4, "搜索与数据 API", ["You.com", "Exa", "Jina", "Brave*", "智慧芽*"]),
        (4, 4, "支付与交易", ["Visa", "masons.ai", "Stripe*", "Adyen*", "Clink*"]),
        (8, 4, "企业知识与本体", ["DataHub", "Datus", "Nowledge"]),
    ], sub="外部连接")
    y -= 6
    layer("", [
        (0, 4, "框架与平台", ["Dify", "Pipecat"]),
        (4, 4, "身份与权限", ["Microsoft", "1Password"]),
    ], sub="框架与治理", rule=False, label_on=False)
    y -= 6
    layer("", [
        (0, 4, "模型网关", ["Raytone*"]),
        (4, 4, "沙箱", ["Daytona"]),
        (8, 4, "存储", ["TiDB", "Tonbo*"]),
    ], sub="运行底座", rule=False, label_on=False)

    o.append(f'<rect x="{LABEL_X}" y="{infra_top + 50}" width="2" height="{y - infra_top - 86}" fill="{BLUE}" opacity="0.3"/>')
    layer("模型", [
        (0, 3, "通用 LLM", ["StepFun", "Kimi", "MiniMax"]),
        (3, 3, "端侧 / 决策模型", ["Liquid|决策模型", "AutoTrust|决策模型*", "AutoArk|端侧 LLM"]),
        (6, 3, "生成模型", ["Tripo|3D、实时视频", "Alaya Lab|AI 游戏引擎*"]),
        (9, 3, "具身与世界模型", ["穹彻", "未来不远", "DYNA", "墨甲", "数耀量生", "World Labs"]),
    ])

    layer("数据与训练", [
        (0, 6, "评测与 RL 数据", ["Arena|agent 轨迹 → RL 环境", "You.com|搜索类 RL 题", "OpenEnv|模拟环境", "Copula|专家数据*", "MindLab|行业模型定制*"]),
        (6, 6, "模型与数据 Infra", ["Baseten|推理", "Google|RL 训练沙箱", "Zilliz|湖库存储", "Langfuse|可观测", "LanceDB|多模态数据"]),
    ])

    o.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{RULE}"/>')
    y += 24
    # legend + footnote
    o.append(f'<rect x="0" y="{y - 13}" width="34" height="18" rx="5" fill="{TAG_FILL}"/>')
    o.append(f'<text x="42" y="{y}" font-size="12" fill="{SUB}">上台演讲</text>')
    o.append(f'<rect x="110" y="{y - 13}" width="34" height="18" rx="5" fill="#fff" stroke="#c9cfd6" stroke-dasharray="3 2.5"/>')
    o.append(f'<text x="152" y="{y}" font-size="12" fill="{SUB}">展区参展商（未上台）</text>')
    o.append(f'<text x="{W}" y="{y}" font-size="12" fill="{SUB}" text-anchor="end">单点工具被收购：Langfuse → ClickHouse，Jina → Elastic，Pipecat → Deepgram</text>')
    y += 14
    head = f'<svg viewBox="-4 0 {W + 8} {y}" xmlns="http://www.w3.org/2000/svg" font-family="{FONT}" style="width:100%;height:auto">'
    return head + "\n" + "\n".join(o) + "\n</svg>"


if __name__ == "__main__":
    open(sys.argv[1], "w", encoding="utf-8").write(landscape())
