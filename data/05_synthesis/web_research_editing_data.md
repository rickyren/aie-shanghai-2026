# 剪辑数据与专家数据市场：外部调研（2026-11-08）

来源均为网页检索。数字多来自媒体、行业博客和招聘聚合站，未经核实，只用来判断方向。

## 一、Copula 现场物料（现场拍摄）
- 产品手册 2026：Visual Coding（Blender 可编辑 3D：保留建模、材质、动画，以及可编辑工程与制作轨迹；Three.js 程序化 3D；Godot 2D 游戏开发；Game3D 原生游戏美术），Cowork（金融长程 Agent RL、法律长程 Agent RL）。**没有视频剪辑。**
- 招聘页：兼职远程专家有金融、法律、3D、UE5、**视频剪辑**。前四类都有对应产品，视频剪辑没有，说明还在筹备。
- 官网招聘页（copulalab.com/careers）同样列有 Video Editing Expert (Part-time, Remote)。

## 二、剪辑方向的外部信号
- **Contra Labs** 在 Hugging Face 发布了 `premiere-video-editing-trajectories` 预览数据集：专业剪辑师在 Adobe Premiere Pro 里制作竖屏短视频时的 computer-use 轨迹，每一步包含截图、结构化动作和第一人称思考。规模很小（4 条轨迹）。https://huggingface.co/datasets/contralabs/premiere-video-editing-trajectories
- **TimelineBench**（2026）：56 个真实剪辑任务，让 agent 把原始素材剪成成片。质量评测用 43 位剪辑师的盲评做校准，测试对象是「前沿模型 + coding agent harness」的组合。https://huggingface.co/datasets/tensortest/timelinebench
- **专家平台在招剪辑类人才**，但多数岗位是标注和评测 AI 生成的视频，不是生产剪辑轨迹：
  - micro1：Video Editor 岗，为教育和机器人类媒体做 AI 训练，要求会 Premiere、AE、FCP、DaVinci。https://jobs.micro1.ai/post/c4e4ac18-a3aa-47ba-8229-d6611085afc6
  - Mercor：招有制片、剪辑、编剧经验的人标注视频片段；另有 Film Studies 方向的多模态评测岗。
  - Outlier（Scale 旗下）：短视频创作、AI 视频质检岗，时薪偏低。
  - Verita AI：主打「品味驱动」的多模态数据和创意人才。https://www.verita-ai.com/
- 时薪区间（第三方聚合站，仅供参考）：剪辑和视频类大约 15–50 美元/小时，法律、医学等专家岗明显更高。
- 没有找到前沿实验室公开采购剪辑工程文件的报道。Adobe 声明不会用 Premiere 用户素材训练模型。

## 三、专家数据和 RL 环境市场的整体情况
- **转向**：数据需求从静态数据集转向 RL 环境。Scale 在 2026 年推出 RL Environments 产品线，称近一半新项目涉及 RL 环境。（新浪财经 2026-10-13）
- **主要玩家**：Scale、Surge、Mercor（2026 年 7 月收购 Deeptune）、Handshake（2026 年 1 月收购 Cleanlab）、micro1、AfterQuery、Mechanize、Prime Intellect；国内有原壤智能 Humanlaya（Talents-AI 专家平台，覆盖并购、法律、临床、合成生物等领域，没有影视）、UniPat，以及从标注转型的海天瑞声、数据堂。
- **报价**（Epoch AI 访谈，行业转述）：单个 RL 任务大约 200–2,000 美元，极少数到 2 万美元；UI gym 类网站环境约每个 2 万美元（SemiAnalysis）；独家环境价格约为非独家的 4–5 倍；头部供应商合同可达每季度七位数美元。
- 来源：https://epoch.ai/gradient-updates/state-of-rl-envs ，https://analyticsindiamag.com/ai-news-updates/complex-reinforcement-learning-tasks-can-cost-up-to-20000-each-epochai-report ，https://finance.sina.com.cn/jjxw/2026-10-13/doc-iniuzqsq0368849.shtml ，https://www.rl-list.com/ ，https://cleverx.com/blog/companies-building-rl-environments-2026/

## 四、对报告的含义
- 剪辑数据处于早期：评测和标注 AI 生成视频的需求已经成形；「agent 在真实剪辑软件里完成任务」的轨迹、环境和 benchmark 刚刚出现（Contra Labs、TimelineBench），Copula 在储备专家。
- 数据形态可以参照 Copula 的 3D 产品，以及 Contra Labs 的做法：任务描述 + 原生工程文件或软件操作轨迹 + 剪辑师校准的质量评分。
