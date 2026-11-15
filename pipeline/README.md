# 脚本说明

供维护数据和页面时查阅。只想阅读内容或重建页面，看仓库根目录的 README 即可。

## 当前使用

| 脚本 | 用途 |
|---|---|
| `validate_data.py` | 检查输入完整性、V3 分析和引用；只读，失败返回非零退出码 |
| `build_site.py` | 校验输入，生成页面，检查链接，再替换输出目录 |
| `check_site.py` | 检查本地 HTML 文件、锚点和重复 ID，不请求外部网站 |
| `stage3_prepare.py` | 从入库转写和标签准备校对输入及议程元数据 |
| `stage4_prepare.py` | 准备 V3 分析 prompt，不执行 LLM 调用 |
| `stage4_aggregate.py` | 校验后汇总 V3 分析为 CSV |
| `review_clean.py` | 校对前后对照；先运行 `stage3_prepare.py` 生成 `_input/` |
| `review_analysis_v3.py` | 生成 V3 复核 HTML，发现问题时返回非零退出码 |
| `landscape.py` | 读取 `landscape.json`，供演讲页和列表使用；首页嵌入已定稿的 `landscape.svg` |
| `landscape_svg.py` | 生成模型、应用和数据商之间关系的示意图 |

`schemas/talk_analysis_v3.json` 同时供 prompt 和程序使用：`properties` / `required` 定义结构，`$defs` 定义枚举，`enums` 保存显示标签。不要在其他脚本里另写一套约束。

## 需要额外输入

`stage0_unify.py`、`stage1_merge.py`、`eval_segmentation.py`、`jev_sample_eval.py` 和 `jev_segment.py` 属于采集、切分和评测阶段，需要未入库的导出或窗口结果。具体输入见各脚本开头。`jev_*` 的 API 调用还需要可选依赖和凭据。`compare_clean.py` 用于比较历史校对结果。

## 历史文件

`review_analysis.py`、`review_analysis_v2.py`、`schemas/talk_analysis.json`、`schemas/talk_analysis_v2.json`、`prompts/analyze_llm.md`、`prompts/analyze_llm_v2.md` 是 V1 / V2 记录。

`render_framework.py` 和 `prompts/synthesize_framework.md` 针对较早的综合草稿，需要仓库中没有的 `framework.md` 等输入。当前首页使用 `report_body.md`；这些旧文件不属于现行构建步骤。

报告和演讲引文只能改整理者的文字与引用位置；不要为了通过校验而改写讲者原文。
