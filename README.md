# AIE Shanghai 2026：从 53 场分享看 AI 行业

AI Engineer Shanghai 2026（2026 年 11 月 5–6 日，上海）的现场同传转写、逐场分析和行业报告。

**适合谁看**：想快速了解这次大会揭示的产业格局和趋势，或者想查某一场分享具体讲了什么的人。
**不适合**：需要精确数字的场景。全部内容来自现场语音识别，数字没有用幻灯片或回放核对过。

## 在线浏览

站点：https://rickyren.github.io/aie-shanghai-2026/

站点分三层：

1. **报告**（`docs/index.html`）：产业版图、核心判断，以及四个方向的结论。文中方括号里的场次编号可以点击，跳到对应的单场页。
2. **全部分享与打标**（`docs/talks.html`）：53 场的逐场分析，包括版图位置、核心 message、骨架、框架、推出的产品、非共识观点、信号、新信息量和推销浓度评分。表格可以搜索、筛选、排序，不含原文。
3. **单场页**（`docs/talks/<场次>.html`）：每场的分析摘要、校对后的转写全文，以及折叠起来的原始识别文本。

## 目录

| 路径 | 内容 |
|---|---|
| `docs/` | 生成好的静态站点，即 GitHub Pages 发布的内容 |
| `data/agenda.csv` | 议程，共 52 场，另有 1 场议程外的分享 |
| `data/00_segments.jsonl` | 同传逐句数据，约 9000 段，包含原文、中英译文和识别时间 |
| `data/01_segment_labels.jsonl` | 逐句切分结果：嘉宾正文、主持串场、场务、噪声；LLM 切分，Jev 交叉校验 |
| `data/01_talks.csv` | 每场的起止位置、时间和字数 |
| `data/02_speakers.csv` | 讲者信息，只取讲者在台上的自述 |
| `data/03_clean/` | 每场的校对清稿（`.md`），以及纠错和存疑记录（`.notes.json`） |
| `data/04_analysis_v3/` | 每场的结构化分析（JSON），字段定义见 `pipeline/schemas/talk_analysis_v3.json` |
| `data/05_synthesis/` | 报告正文、展商信息、偏宣传场次名单、剪辑数据外部调研，以及各方向逐条附原文的证据表（`sections/`） |
| `pipeline/` | 处理脚本和 prompt |

## 处理流程

1. **统一**：合并 TransGull 同传 API 数据，用识别时间排序（`stage0_unify.py`）。
2. **切分**：LLM 按窗口逐段标注正文、串场、场务，并对应到议程场次；TypeSafe Jev 逐段打分做交叉校验，两者一致率 97.5%（`stage1_merge.py`、`jev_segment.py`）。
3. **校对**：逐场修正专有名词、去掉口头语，存疑的专有名词联网核实（`stage3_prepare.py` + `prompts/clean_llm.md`）。
4. **分析**：先还原讲者意图和演讲骨架，再提取框架、产品、非共识观点和信号，过滤掉行业共识（`prompts/analyze_llm_v3.md`）。
5. **综合**：每个方向回到原文逐条核实，结论附上原文引用（`data/05_synthesis/sections/*_evidence.md`）。
6. **生成站点**：`python pipeline/build_site.py . docs`

## 说明

- 原始抓取数据不在仓库里，因为里面有分享链接的凭据。`stage0_unify.py` 需要这份数据才能重跑；其他步骤都可以从 `data/` 开始。
- 转写内容的版权属于各位讲者和大会主办方，本仓库只用于学习和研究。如果有讲者希望撤下内容，请提 issue。
- 「（推断）」标记的是分析者的推断，不是讲者原话。展商信息来自展商官网和现场物料，展商没有上台演讲。
