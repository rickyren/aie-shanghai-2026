"""Generate the two SVGs used in the report: the industry landscape and the data/integration loop.

Usage: python3 -I pipeline/landscape_svg.py <landscape_out.svg> <integration_out.svg>

Palette: the landscape is black/grey only (it has no arrows, so blue would carry no meaning);
the integration loop uses blue for its arrows and their labels.
Entities ending with "*" are expo exhibitors and render in grey (upright, not italic).

One entity per line: cells with 2-3 entities stack them in a single column; multiple columns
only for 4+ entities, each column at least 2 rows, separated by a wide COLGAP.

Layout is content-driven: every cell is measured (approximate SF/PingFang advance widths),
cells get their natural width plus an equal share of the row's slack, and row heights follow
the tallest cell. The viewBox is 960 wide so 1 unit = 1 px in the report's text column.
"""
import math
import sys

FONT = "-apple-system,'PingFang SC','Helvetica Neue',sans-serif"
INK, ENT, SUB, EXH = "#1f2328", "#2d333a", "#57606a", "#9aa0a6"
LINE, CELL_FILL, CELL_LINE = "#d0d7de", "#f6f8fa", "#e3e6ea"
BLUE = "#2f5bd3"

# type scale: layer title > cell title > entity > notes
T_LAYER, T_CELL, T_ENT, T_NOTE = 16, 14, 13, 12.5
STEP = 20          # entity line pitch
PAD = 12           # cell inner padding
BPAD = 12          # box inner padding (sides and bottom)
GAP = 8            # gap between cells
COLGAP = 28        # gap between entity columns inside a cell (wide, so columns never read as one name)
BOX_GAP = 14       # gap between layer boxes
TITLE_H = 38       # box title band (title baseline at +25)
W = 960
DEBUG = False


# ---------------------------------------------------------------- text metrics
def char_w(ch):
    o = ord(ch)
    if o >= 0x2E80 or ch in "：，、（）→":
        return 1.0
    if ch == " ":
        return 0.27
    if ch in "il.,:;'|!·":
        return 0.26
    if ch in "jft()/-":
        return 0.34
    if ch == "r":
        return 0.38
    if ch in "mw":
        return 0.84
    if ch in "MW":
        return 0.9
    if ch.isupper():
        return 0.66
    if ch.isdigit():
        return 0.6
    return 0.55


def tw(s, size):
    return sum(char_w(c) for c in s.rstrip("*")) * size


# ---------------------------------------------------------------- primitives
def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size=T_ENT, color=INK, weight=None, anchor=None, extra=""):
    w = f' font-weight="{weight}"' if weight else ""
    a = f' text-anchor="{anchor}"' if anchor else ""
    return f'<text x="{r(x)}" y="{r(y)}" font-size="{size}" fill="{color}"{w}{a}{extra}>{esc(s)}</text>'


def r(v):
    v = round(v, 1)
    return int(v) if v == int(v) else v


def entity(x, y, s, anchor=None):
    return text(x, y, s[:-1], color=EXH, anchor=anchor) if s.endswith("*") else text(x, y, s, color=ENT, anchor=anchor)


def rect(x, y, w, h, rx, fill, stroke, sw=1):
    return f'<rect x="{r(x)}" y="{r(y)}" width="{r(w)}" height="{r(h)}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def box(x, y, w, h, title):
    return [rect(x, y, w, h, 10, "#fff", LINE, 1.2), text(x + BPAD + 2, y + 25, title, T_LAYER, INK, 700)]


def columns(items, ncols):
    """column-major split; earlier columns take the remainder (7 in 3 cols -> 3, 2, 2)"""
    base, extra = divmod(len(items), ncols)
    out, i = [], 0
    for c in range(ncols):
        n = base + (1 if c < extra else 0)
        out.append(items[i:i + n])
        i += n
    return [c for c in out if c]


def cols_width(cols):
    return sum(max(tw(e, T_ENT) for e in c) for c in cols) + COLGAP * (len(cols) - 1)


def col_positions(x, w, cols):
    """entity columns pack left with a fixed COLGAP (spreading them apart broke up pairs)"""
    xs, cx = [], x + PAD
    for col in cols:
        xs.append(cx)
        cx += max(tw(e, T_ENT) for e in col) + COLGAP
    return xs


def cell_h(nlines):
    return 43 + (nlines - 1) * STEP + 14


class Cell:
    def __init__(self, title, items, ncols=1):
        # one-entity-per-line rule: 2-3 entities always stack; extra columns need >= 2 rows each
        if len(items) < 4:
            ncols = 1
        ncols = max(1, min(ncols, len(items) // 2))
        self.title, self.cols = title, columns(items, ncols)
        self.lines = max(len(c) for c in self.cols)

    @property
    def natural(self):
        return max(tw(self.title, T_CELL) + 6, cols_width(self.cols)) + 2 * PAD

    def render(self, x, y, w, h, col_xs=None):
        out = [rect(x, y, w, h, 7, CELL_FILL, CELL_LINE), text(x + PAD, y + 22, self.title, T_CELL, INK, 600)]
        for cx, col in zip(col_positions(x, w, self.cols), self.cols):
            for i, e in enumerate(col):
                out.append(entity(cx, y + 43 + i * STEP, e))
        return out


class Panel(Cell):
    """untitled cell for layers without sub-categories; entities centred vertically"""
    def __init__(self, items, ncols=1):
        super().__init__("", items, ncols)

    @property
    def natural(self):
        return cols_width(self.cols) + 2 * PAD

    def render(self, x, y, w, h, col_xs=None):
        out = [rect(x, y, w, h, 7, CELL_FILL, CELL_LINE)]
        y0 = y + h / 2 - (self.lines - 1) * STEP / 2 + 4.5
        for cx, col in zip(col_positions(x, w, self.cols), self.cols):
            for i, e in enumerate(col):
                out.append(entity(cx, y0 + i * STEP, e))
        return out


def boxes_row(x0, x1, y, groups, cell_height):
    """groups: [(title, [cells])]. Boxes sit side by side; every cell in the row gets
    its natural width plus the same share of the slack. Returns (svg parts, box height, cell x list)."""
    ncells = sum(len(g[1]) for g in groups)
    fixed = sum(2 * BPAD + GAP * (len(g[1]) - 1) for g in groups) + BOX_GAP * (len(groups) - 1)
    slack = (x1 - x0) - fixed - sum(c.natural for g in groups for c in g[1])
    share = slack / ncells
    if DEBUG:
        print("row", [g[0] for g in groups], "slack/cell", round(share, 1), file=sys.stderr)
    bh = TITLE_H + cell_height + BPAD
    out, x, cell_xs = [], x0, []
    for title, cells in groups:
        widths = [c.natural + share for c in cells]
        bw = sum(widths) + GAP * (len(cells) - 1) + 2 * BPAD
        cx = x + BPAD
        for w in widths:
            cell_xs.append(cx)
            cx += w + GAP
        out += box(x, y, bw, bh, title)
        out += render_row(x + BPAD, y + TITLE_H, cells, widths, cell_height)
        x += bw + BOX_GAP
    return out, bh, cell_xs


def row_widths(cells, span):
    """natural width + an equal share of the slack, so every cell carries the same spare room"""
    nat = [c.natural for c in cells]
    slack = span - GAP * (len(cells) - 1) - sum(nat)
    return [n + slack / len(cells) for n in nat], slack


def render_row(x0, y, cells, widths, h):
    out, x = [], x0
    for c, w in zip(cells, widths):
        out += c.render(x, y, w, h)
        x += w + GAP
    return out


def arrow_defs(mid):
    return (f'<defs><marker id="{mid}" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="9" markerHeight="9" '
            f'orient="auto" markerUnits="userSpaceOnUse"><path d="M0,0.5 L10,5 L0,9.5 z" fill="{BLUE}"/></marker></defs>')


# ---------------------------------------------------------------- landscape
def landscape():
    L, R = 1, W - 1                # full width; 1 unit keeps the outer strokes inside the viewBox
    o = []
    y = 1

    # 1. AI 应用 + 企业内部落地 -------------------------------------------------
    app_cells = [
        Cell("通用 / 个人 agent", ["Manus", "OpenClaw", "YouMind"]),
        Cell("垂直行业", ["Harvey：法律", "AhaCreator：达人营销", "Cookiy：用户研究", "HeyGen：视频",
                       "CHILING：美妆", "KouShi：语言学习", "HellYeah：广告投放*"], 3),
    ]
    ent = Panel(["Optiver：交易公司", "Techcombank：银行", "Agoda：旅游平台", "Instagram：社交", "HICAP：制造", "Data4Life：医疗"], 2)
    part, bh, top_xs = boxes_row(L, R, y, [("AI 应用", app_cells), ("企业内部落地", [ent])], cell_h(3))
    o += part
    y += bh + BOX_GAP

    # 2. Agent Infra: three labelled sub-rows, outermost layer on top ----------------
    label_w = tw("框架与治理", 13) + 20
    gx0, gx1 = L + BPAD + label_w, R - BPAD
    sub = [
        ("外部连接", [Cell("搜索与数据 API", ["You.com", "Exa", "Jina", "Brave*", "智慧芽*"], 2),
                  Cell("支付与交易", ["Visa", "masons.ai", "Stripe*", "Adyen*", "Clink*"], 2),
                  Cell("企业知识与本体", ["DataHub", "Datus", "Nowledge"])]),
        ("框架与治理", [Cell("框架与平台", ["Dify", "Pipecat"]),
                   Cell("身份与权限", ["Microsoft", "1Password"])]),
        ("运行底座", [Cell("模型网关", ["Raytone*"]),
                  Cell("沙箱", ["Daytona"]),
                  Cell("存储", ["TiDB", "Tonbo*"])]),
    ]
    # the two three-cell rows share one column grid so their cell edges line up. The right
    # column starts exactly under the 企业内部落地 cell (企业知识与本体 relates to it); the
    # other two split the rest by natural size + equal slack. The middle row reuses the grid.
    three = [cells for _, cells in sub if len(cells) == 3]
    nat = [max(c.natural for c in col) for col in zip(*three)]
    right = gx1 - top_xs[-1]
    assert right >= nat[2], "right infra column narrower than its content"
    gslack = (top_xs[-1] - GAP - gx0) - GAP - nat[0] - nat[1]
    grid = [nat[0] + gslack / 2, nat[1] + gslack / 2, right]
    rows_h = [cell_h(max(c.lines for c in cells)) for _, cells in sub]
    ih = TITLE_H + sum(rows_h) + GAP * (len(sub) - 1) + BPAD
    o += box(L, y, R - L, ih, "Agent Infra")
    ry = y + TITLE_H
    for (label, cells), h in zip(sub, rows_h):
        o.append(text(L + BPAD + 2, ry + h / 2 + 4.5, label, 13, SUB, 600))
        # middle row: 框架与平台 spans the first two grid columns, 身份与权限 sits in the right one
        widths = grid if len(cells) == 3 else [grid[0] + GAP + grid[1], grid[2]]
        if DEBUG:
            print("infra", label, [round(w) for w in widths], file=sys.stderr)
        o += render_row(gx0, ry, cells, widths, h)
        ry += h + GAP
    y += ih + BOX_GAP

    # 3. 模型 -------------------------------------------------------------------
    m_cells = [
        Cell("通用 LLM", ["StepFun", "Kimi", "MiniMax"]),
        Cell("端侧、决策模型", ["Liquid：决策模型", "AutoTrust：决策模型*", "AutoArk：端侧 LLM"]),
        Cell("生成模型", ["Tripo：3D、实时视频", "Alaya Lab：AI 游戏引擎*"]),
        Cell("具身与世界模型", ["穹彻", "未来不远", "DYNA", "墨甲", "数耀量生", "World Labs"], 2),
    ]
    ch = cell_h(max(c.lines for c in m_cells))
    mh = TITLE_H + ch + BPAD
    o += box(L, y, R - L, mh, "模型")
    widths, ms = row_widths(m_cells, R - L - 2 * BPAD)
    if DEBUG:
        print("models slack/cell", round(ms / 4, 1), file=sys.stderr)
    o += render_row(L + BPAD, y + TITLE_H, m_cells, widths, ch)
    y += mh + BOX_GAP

    # 4. 评测与 RL 数据 + 模型与数据 Infra ---------------------------------------------
    ev = Panel(["Arena：agent 轨迹 → RL 环境", "You.com：搜索类 RL 题", "OpenEnv：模拟环境",
                "Copula：专家数据、RL 环境*", "MindLab：帮行业公司做数据和后训练*"], 2)
    mi = Panel(["Baseten：推理", "Google：RL 训练沙箱", "Zilliz：湖库存储", "Langfuse：可观测", "LanceDB：多模态数据"], 2)
    part, dh, _ = boxes_row(L, R, y, [("评测与 RL 数据", [ev]), ("模型与数据 Infra", [mi])], 22 + 2 * STEP + 14)
    o += part
    y += dh

    # footnote + grey-exhibitor note on one line -------------------------------------
    fy = y + 24
    o.append(text(L + 2, fy, "单点工具被收购：Langfuse → ClickHouse，Jina → Elastic，Pipecat → Deepgram", T_NOTE, SUB))
    o.append(text(R - 2, fy, "灰字：展区参展商（未上台演讲）", T_NOTE, EXH, anchor="end"))
    H = fy + 8
    head = f'<svg viewBox="0 0 {W} {r(H)}" xmlns="http://www.w3.org/2000/svg" font-family="{FONT}" style="width:100%;height:auto">'
    return "\n".join([head] + o + ["</svg>"])


# ---------------------------------------------------------------- integration loop
def loop():
    """Two-way integration: model labs move up, vertical apps/enterprises move down; data vendors sell to both."""
    o = []
    NX, NW, NH = 36, 420, 76

    def node(x, y, w, h, title, rows):
        out = [rect(x, y, w, h, 10, "#fff", LINE, 1.2), text(x + w / 2, y + 30, title, T_LAYER, INK, 700, "middle")]
        for i, s in enumerate(rows):
            out.append(text(x + w / 2, y + 54 + i * STEP, s, T_ENT, ENT, None, "middle"))
        return out

    top_y, bot_y = 10, 10 + NH + 96
    o += node(NX, top_y, NW, NH, "垂直应用与企业", ["Harvey · Agoda · Techcombank · 药企、金融公司"])
    o += node(NX, bot_y, NW, NH, "模型公司", ["StepFun · Kimi · MiniMax · 前沿实验室"])
    dh = 30 + 2 * STEP + 24 + 14
    dx, dw = W - 36 - 280, 280
    dy = (top_y + bot_y + NH) / 2 - dh / 2
    o += node(dx, dy, dw, dh, "数据商", ["专家数据：Copula、MindLab", "评测平台：Arena", "搜索公司：You.com"])

    dash = 'stroke-dasharray="6 4"'
    g0, g1 = top_y + NH, bot_y
    mid = (g0 + g1) / 2
    ux, dxa = NX + NW / 2 - 56, NX + NW / 2 + 56
    # upward: labs absorb harness and ship first-party apps
    o.append(f'<path d="M{ux},{g1} V{g0 + 1.5}" stroke="{BLUE}" stroke-width="2" {dash} fill="none" marker-end="url(#ab-i)"/>')
    o.append(text(ux - 12, mid - 14, "上行整合", T_CELL, BLUE, 700, "end"))
    o.append(text(ux - 12, mid + 6, "harness 能力内化进模型", 12.5, BLUE, None, "end"))
    o.append(text(ux - 12, mid + 25, "第一方应用进入应用层", 12.5, BLUE, None, "end"))
    # downward: apps and enterprises post-train open models on their own data
    o.append(f'<path d="M{dxa},{g0} V{g1 - 1.5}" stroke="{BLUE}" stroke-width="2" {dash} fill="none" marker-end="url(#ab-i)"/>')
    o.append(text(dxa + 12, mid - 14, "下行自训", T_CELL, BLUE, 700))
    o.append(text(dxa + 12, mid + 6, "开源模型 + 自有数据", 12.5, BLUE))
    o.append(text(dxa + 12, mid + 25, "后训练", 12.5, BLUE))
    # data vendors sell to both sides (elbow arrows, labels outside the lines)
    cx = dx + dw / 2
    ty, by = top_y + NH / 2, bot_y + NH / 2
    o.append(f'<path d="M{cx},{r(dy)} V{r(ty)} H{NX + NW + 1.5}" stroke="{BLUE}" stroke-width="2" fill="none" marker-end="url(#ab-i)"/>')
    o.append(text((NX + NW + cx) / 2, ty - 9, "行业模型定制（MindLab）", 12.5, BLUE, 600, "middle"))
    o.append(f'<path d="M{cx},{r(dy + dh)} V{r(by)} H{NX + NW + 1.5}" stroke="{BLUE}" stroke-width="2" fill="none" marker-end="url(#ab-i)"/>')
    o.append(text((NX + NW + cx) / 2, by + 20, "垂直数据与 RL 环境（Copula、Arena、You.com）", 12.5, BLUE, 600, "middle"))
    H = bot_y + NH + 10
    head = f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="{FONT}" style="width:100%;height:auto">'
    return "\n".join([head, arrow_defs("ab-i")] + o + ["</svg>"])


if __name__ == "__main__":
    DEBUG = "--debug" in sys.argv
    sys.argv = [a for a in sys.argv if a != "--debug"]
    open(sys.argv[1], "w", encoding="utf-8").write(landscape())
    open(sys.argv[2], "w", encoding="utf-8").write(loop())
