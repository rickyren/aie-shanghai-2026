# AIE Shanghai 2026 参会笔记

AI Engineer Shanghai 2026（11 月 5–6 日）的演讲转写、摘要和参会笔记。

**给谁看**：查某场演讲，或了解会上讨论的产品和工程实践。只想阅读，打开下面的页面即可；后面的命令供维护仓库时使用。数字来自现场语音识别，未用幻灯片或回放核实，不适合拿来做精确比较。

## 阅读

- [参会笔记](https://rickyren.github.io/aie-shanghai-2026/)：参会机构、模型与应用公司的变化、四个主题的工程实践。
- [全部演讲](https://rickyren.github.io/aie-shanghai-2026/talks.html)：53 场的摘要，可搜索、筛选和排序。
- 单场页面：摘要、校对后的转写、原始识别文本。「查看原文」会定位到对应转写段落；段落后的链接可查看原始识别文本。

## 本地构建

需要 **Python 3.12 或更新版本**。先用 `python3 --version` 确认版本；如果系统默认的 Python 太旧，以下命令中的 `python3` 请换成新版 Python 的路径。

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python pipeline/build_site.py . out/site
open out/site/index.html
```

构建只读取已入库数据，不调用 LLM、Jev 或联网调研。它会先校验输入，再在临时目录生成全部页面并检查站内链接。全部通过后才替换输出目录；失败时保留旧页面。`out/` 已忽略。

更新仓库内的静态页面：

```bash
.venv/bin/python pipeline/build_site.py . docs
```

这只改本地文件，不会推送或发布。

## 检查

```bash
.venv/bin/python pipeline/validate_data.py .
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python pipeline/check_site.py docs
```

检查范围包括：场次和输入文件是否齐全、转写与标签是否一一对应、V3 字段类型和评分范围、引用是否出现在标注的段落、版图是否覆盖全部场次，以及 HTML 文件和锚点链接是否有效。发现问题返回非零退出码。

编辑单场分析时，可以先检查这一场：

```bash
.venv/bin/python pipeline/validate_data.py . --talk d1m05
```

CI 会运行全量校验、回归测试、重建站点，并确认提交的 `docs/` 和分析 CSV 与源数据一致。

## 修改摘要或笔记

当前分析格式是 **V3**。

1. 修改单场分析：编辑 `data/04_analysis_v3/<file_id>.json`，字段约束见 `pipeline/schemas/talk_analysis_v3.json`（标准 JSON Schema）。
2. 修改首页文字：编辑 `data/05_synthesis/report_body.md`。
3. 修改机构分类或图中实体：编辑 `data/05_synthesis/landscape.json`。列表筛选和单场分类读取这份数据。首页直接嵌入同目录的定稿 `landscape.svg`，修改图中机构时需同步两个文件。`value_chain_layer` 保留分析阶段的原始标签，最终展示以 `landscape.json` 为准。
4. 重新生成 CSV 和页面，再运行检查：

```bash
.venv/bin/python pipeline/stage4_aggregate.py .
.venv/bin/python pipeline/build_site.py . docs
```

需要重新准备分析任务时：

```bash
.venv/bin/python pipeline/stage3_prepare.py .
.venv/bin/python pipeline/stage4_prepare.py .
```

第一条生成逐场原文、议程元数据和校对 prompt；第二条生成 `data/04_analysis_v3/_input/*.prompt.md`。也可在命令末尾指定单场。脚本只准备输入，LLM 校对、分析和综合是独立的人工或 agent 工作，不会被这些命令自动执行。

V1、V2 的 prompt、schema 和复核脚本仅为历史记录，当前构建不使用。更多脚本说明见 [pipeline/README.md](pipeline/README.md)。

## 数据和复现范围

| 路径 | 内容 |
|---|---|
| `docs/` | 已生成的静态页面 |
| `data/agenda.csv` | 52 场议程，另有 1 场议程外分享 |
| `data/00_segments.jsonl` | 9,071 段原始转写及译文 |
| `data/01_segment_labels.jsonl` | 正文、主持串场、场务和噪声标签，以及所属场次 |
| `data/01_talks.csv` | 场次、讲者、段落范围和时间 |
| `data/02_speakers.csv` | 讲者自述信息 |
| `data/03_clean/` | 校对转写及纠错、查证和存疑记录 |
| `data/04_analysis_v3/` | 逐场结构化分析 |
| `data/05_synthesis/` | 首页正文、机构分类、展商资料、证据表和外部调研 |

从已入库数据可以离线重建站点、汇总 CSV、校验分析，以及准备逐场校对和分析输入。以下上游步骤需要额外材料，不能仅靠本仓库从头复现：

- `stage0_unify.py` 需要 `raw/refetch_20261108/` 中的 TransGull API 导出。原始导出包含分享链接凭据，不入库。
- `stage1_merge.py` 需要原始 LLM 窗口结果 `data/seg_llm/` 和补充评测窗口 `data/eval_1h/llm_labels.json`；Jev 交叉校验还需要 `data/seg_jev/`。这些中间结果未入库。脚本会在缺少必要输入时停止，不覆盖已提交的标签。
- `jev_segment.py` 会调用付费 API，需要单独安装 `requirements-jev.txt`，并通过环境变量或 macOS Keychain 提供 `TYPESAFE_API_KEY`。重建站点无需安装它，也无需凭据。

## 内容说明

转写版权属于讲者和大会主办方，本仓库用于学习和研究。讲者如需撤下内容，可提 issue。

「（推断）」是整理者的判断，不是讲者原话。展商资料来自官网和现场物料，展商没有上台演讲。讲者阵容由主办方和赞助商决定，本页不能代表整个行业。
