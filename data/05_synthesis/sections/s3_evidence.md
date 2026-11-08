# s3 证据表：数据供给

用途：s3_revised.md 和 core_revised.md 的每条论断都能在这里找到原文。引文逐字摘自 `data/03_clean/*.md`，展商信息摘自 `exhibitors.csv`。
标记：**keep** 保留；**merge → X** 并入某条；**drop** 删除并写原因。substance_filter 中标为宣传的演讲只作市场事实使用，已注明。

---

## A. 谁在卖数据

### A1. Arena：免费 agent 产品产出轨迹，卖评测、私测和 RL 环境给它排名的模型公司 — **keep**
- d1m07 [seg 1165–1166]："Unlike many static benchmarks, which use a predefined problem set to evaluate model performance — which is very easy to game and also to saturate — Arena took a very different approach to evaluation. We rely on millions of users who come to our consumer platform, arena.ai, to access AI models, perform real personal and work-related tasks, and contribute very valuable feedback signals, which we can then harvest and turn into accurate and reliable evaluation products and our leaderboards."
- d1m07 [seg 1174]："What this means is that Arena's agent mode becomes an endless source of very high-quality data based on real-world agent use, from which we can harvest and mine important signals and turn them into a reliable agent evaluation product."
- d1m07 [seg 1189]："We trained a user simulator on the millions of sessions that happened in Arena's agent mode … Arena is also working on turning some of the agent traces into rubrics and RL environments to help labs with post-training. Eventually we hope to provide a closed-loop flywheel that goes from evals to actionable insights to post-training products, such as rubrics and RL environments, that help labs actually improve the performance of their models."
- d1m07 [seg 1192]："For frontier labs and new labs, which are our customers … we can work with you on co-releasing models, co-marketing, and private testing and private evaluation of your model checkpoints before you launch them publicly. And last but not least, we're building post-training data products, such as RL environments, to help these labs improve the performance of their models."
- 判断：Arena 的主业是榜单公信力，卖点是「真实数据、难刷」。它的客户就是被排名的模型公司，卖的 RL 环境又来自同一批 agent 轨迹。（推断）卖得越多，榜单越像「训练过的考题」，中立性被削弱。这是讲者没说、但结构上成立的张力。

### A2. You.com：用自家 web graph 合成搜索类可验证 RL 题，帮模型学会用它的搜索 — **keep**
- d1m05 [seg 933–941]："We focus on providing LLMs pre-training data, post-training data, and web search at inference. So we partner with these labs: we are their search lab, they are the model lab."
- d1m05 [seg 1002–1008]："因为You.com有自己的互联网搜索API，我们其实有一个东西叫web graph……这样我们可以自己算一些像Google或者Bing的PageRank这样的分数，或者agentic relevance的分数。"
- d1m05 [seg 1009–1014]："你要看中间popularity的网站来做这个data set。"
- d1m05 [seg 1032–1039]："这1500个RL task都是用我们的web graph和搜索API来做的……这里全部是RLVR。"
- d1m05 [seg 1065–1072]："one, start with strong tools — in this case we started with strong search, but you want to start with a strong tool for anything that you're doing. Build questions with representative datasets, or in this case build questions from the real web. Filter by difficulty…"
- d1m05 [seg 974–980]："但最重要的其实是你的RL data set。这个RL data set在你做后训练的时候，其实比tooling或者environment更重要。"
- 判断：搜索公司的数据来自索引本身（web graph 选中等热度网页出题），用来训练模型在它的搜索工具上做研究。（推断）这类数据加强绑定：模型在它的工具上学会了搜索。

### A3. You.com 的副作用：训练后的模型搜索调用大幅减少 — **keep**（作为 A2 的反面）
- d1m05 [seg 1046–1049]："you don't reward the model for efficiency. But because the model learns more about how to use the relevant tools … it actually becomes more efficient as a side effect."
- d1m05 [seg 1056–1064]："看这个后训练之前最基本的model来回答这个task，它用了313个tool call，一共用了150个搜索……但是你看后训练之后这个模型的behavior：一共只用了7个tool call，3个互联网搜索……它学到了：要是你拿到答案，你可以做一些verification，不用再continuously搜索。"
- d1m05 [seg 913–922]（计费单元是 API 调用）："primarily, the base of what we do is we provide our search engine through an API for your agent, your LLM, to search the web."
- 判断：（推断）按调用计费的搜索公司，卖 RL 数据让模型每题少搜很多次。绑定加强，单任务调用量下降。数字不引用，只说「工具调用和 token 消耗大幅下降」。

### A4. You.com 不用客户查询训练 — **drop**
- d1m05 [seg 923–932]："We don't train on your data, so you're safe with us."
- 原因：标准的企业 ZDR 承诺，常识，对本节判断没有增量。

### A5. Copula Lab（展商）：专家数据、RL 环境、benchmark，客户是前沿模型和垂直 agent 团队 — **keep**
- exhibitors.csv："专家数据、RL 环境、benchmark，服务前沿模型和垂直 agent 团队；数据产品含 Blender 3D、Three.js、Godot 游戏、游戏美术、网页开发、金融/法律长程任务；兼职专家招聘含视频剪辑、3D、游戏开发、金融、法律"
- 判断：数据就是主业，卖数据不伤自己。被编码的是兼职专家所在行业的手艺。金融、法律长程任务正好是 Harvey 这类垂直应用的领域（见 B1）。

### A6. Copula 招视频剪辑兼职专家，剪辑数据可能的形态 — **keep**（压缩，归入「自杀式」那一点）
- exhibitors.csv：兼职专家招聘含「视频剪辑」，与 3D、游戏开发并列；数据产品含 Blender 3D、Godot 游戏。
- 旁证 d1m20 [seg 2196–2202]："现在有很多 long horizon 的 benchmark……会发现里面很多具体的 task 是提供一个沙箱环境，要求 AI agent 直接交付一个具体的结果，而不是像以前一样，给你一个 chat 对话框，交付一段代码片段。"
- d1m20 [seg 2203–2206]："这是里面的一个测试场景，一个 RPG Maker 的界面……再比如其他例子，去操作具体的游戏引擎，除此之外还有操作很多其他具体的软件，比如 Blender。"（d1m20 被标为宣传，此处只用作市场事实：长程 benchmark 已经包含「在具体软件里交付成品」的任务。）
- 判断：（推断）剪辑数据大概率也是「任务描述＋剪辑工程文件＋专家对成片的评分」，在沙箱里的剪辑软件交付成片。现文这段保留，删掉重复的说明。

### A7. MindLab（展商）— **keep，但纠正归类**
- exhibitors.csv："为药企、金融、政务、游戏公司做 benchmark、数据开发、后训练、推理部署，把行业经验变成专有模型能力"
- 判断：现文把 MindLab 写成「卖给模型公司」，是**误归类**。它的客户是行业公司，帮它们把行业经验留在自己的专有模型里。方向和 Copula 相反，应归入「帮垂直行业自用」。

### A8. 推理时卖数据的公司：Exa、Brave（展商）、Patsnap（展商）、Jina Reader、You.com 授权数据 — **keep**（只进核心表一行）
- d1m05 [seg 913–922]："We also have licensed structured data sources of information not found on the web, from things like the World Bank and S&P and Polymarket…"
- exhibitors.csv Patsnap："20 亿+ 专利、科研、生物医药等垂直数据，经 API / MCP 提供给 agent"；Brave："搜索（Brave Search API）"
- d2m20 [seg 3760–3766]："各个网站做反爬的出发点可能不一样：大站主要是想保护数据，而小站，像我们 Reader，主要是想节省 IT 资源。"
- d2m20 [seg 3775–3786]："'给钱就能抓'也并不会真正实现，因为其实有一个灰黑产的问题：如果真的给钱就能抓的话，很难防止数据倒卖。"
- 判断：按次卖访问权，数据资产不出手。和训练数据的区别有价值，但不是本节重点。进核心表一行，正文不展开。d1m14 Exa 全篇没讲训练数据，且被标为宣传，不单列。

### A9. 现文「已经能看到的数据品类」清单 — **merge → A5**
- 判断：这是 Copula 产品页加 You.com、Arena 的罗列，单列成段是凑覆盖面。并入 A5 的表格行。

### A10. Google 开源 RL 沙箱：前沿实验室都在做 RL，瓶颈在沙箱调度 — **drop**
- d1m19 [seg 2083–2091]："今天所有这些前沿实验室都在做强化学习训练，并且规模越来越大……这个基础设施，其实就是如何持续调度大规模的沙箱。"
- 原因：substance_filter 标为宣传；讲的是 RL 基础设施，与谁卖数据无关；「实验室在做 RL」是常识。

---

## B. 谁只自用、不卖

### B1. Harvey：内部 agent 的 PR 做评测集，自己做法律 benchmark，自己后训练 open-weight 模型 — **keep**
- d1b02 [seg 194–204]："我们也针对法律的各种场景做过一些 benchmark，也就是评测集：24 年就开始做 Big Law Bench，到今年做了 Legal Agent Bench……我们也对 open weight model 做了一些 post training，包括 GLM 或者 Kimi K3 这些。"
- d1b02 [seg 214–215]："我们根据这上万个 PR 得到的结果，成为了我们现在可以用的评测集。"
- d1b02 [seg 226–232]："一旦我们有了这么一个大家都可以协作的 Agent，这就成了我们可以在线上收集的数据，并且是内部数据，我们可以更好地做一些实验。"
- d1b02 [seg 319–324]："所以你要相信你自己公司内部数据的 eval，而不是别人给你的 benchmark。"
- 判断：垂直应用把数据变成两样东西：选模型用的评测集，和后训练开源模型的材料。它在向下整合，没有向模型公司卖。

### B2. Langfuse：最好的团队开始用自己的标注建 RL 环境，训练自己的开源模型 — **keep**（并入 B1 那一点）
- d1m03 [seg 624–628]："when you run this loop — write evals, label data — you collect a lot of data that's incredibly valuable. It's a unique, application-specific dataset … the next step that we see the best teams starting to take right now is to build their own reinforcement learning environments, because the labels you get from running the improvement loop are signals you can use to build tasks, build verifiers, and in the end train your own open-source models that saturate on task quality for what you need."
- 判断：可观测平台看到的客户趋势，和 Harvey 互证。

### B3. Agoda：已合并 MR 回放成自家仓库的 benchmark，用来「训练 agent」 — **keep**（并入自用那一点）
- d1b07 [seg 907]："we should focus on our own benchmark and our own repositories."
- d1b07 [seg 919–924]："you should start to use your merged MRs to train your agent."
- 判断：这里的「train」指改 context 补丁（[seg 911]："The output we expect from the skill is a context MR"），不是训练权重。只作「自用」例子，不说它训模型。

### B4. Cookiy：历史坏案例做 benchmark，明确不做后训练 — **keep**（作为自用的另一端）
- d1b06 [seg 830–838]："我们把所有这种场景全部抓下来，历史以来可能积累了几千个这样的案例，然后把这些样例做成我们的 benchmark。"
- d1b06 [seg 861–872]："不要说'这个 harness 到头了，我们就自己去 post-train 一个模型'……我们坚持不做这件事情……我不觉得在接下来一年之内我需要自己去 fine-tune 或者 post-train 任何模型"
- 判断：同样自用，但只用在 harness 上。和 Harvey 构成自用的两种程度。

### B5. KouShi：用自己用户的音频评测 STT — **drop**
- d2m06 [seg 1135–1138]："run your models on your own users' audio"
- 原因：「公开 benchmark 不代表你的场景」是常识；对数据供给判断没有增量。B1 已足够代表。

### B6. OpenClaw ShellBench：自建 benchmark，只公开一小部分 — **drop**
- d1m10 [seg 586–597]："It's 135 tasks, and a small subset will be public."
- d1m10 [seg 598–601]："One thing we're seeing a lot of companies doing now is developing their own internal benchmarks."
- 原因：讲者没说为什么只公开一部分，用它论证「防止被训练」属于过度推断。「公司在建内部 benchmark」与 B1 重复。

### B7. StepFun 自建 Step Code Bench — **merge → C 段 StepFun**
- d1m09 [seg 398–407]："我们在内部构建了Step Code Bench……这个bench覆盖的仓库、领域、语言以及任务都是我们自定义的。"（d1m09 被标为宣传，只作市场事实。）

### B8. Nowledge：把团队 context 内化进模型参数，九个实验只有三个有收益，改为编译进 harness — **drop**
- d2m19 [seg 3630–3653]："我们第一个尝试是，能不能把 team context 这些团队的智慧，一定程度上内化到你的参数模型中……只有三个情况是有收益的……我们发现最好的方式是让 team context 以 harness adapter 的方式被 leverage。"
- 原因：讲的是自家团队知识放在哪一层，与向模型公司供数据关系弱；单一实验，细节未展开。

### B9. 机器人公司自采数据（穹彻、未来不远、LanceDB）— **drop**
- d2m14 [seg 2730–2739]："我们已经完全放弃了生产级别的人工质检、标注……我们认为至少在具身这样的场景里，人类标注员不具备实践的价值。"
- 原因：具身公司自己就是模型方，自采自训，不是数据卖家；离本节主线远。

---

## C. 模型公司的吸收和向上整合

### C1. 投资人：吞掉应用的是模型公司的第一方应用，且有 token 补贴 — **keep**
- d2m07 戴雨森 [seg 1178–1185]："其实我们看到所谓吞食小应用公司的，我认为并不是模型本身，而是模型公司自己做的第一方应用，比如 Claude Code、Codex、ChatGPT。它们本质上也是应用，并且是第一方做的，并且它们补贴了 20 倍的 token，对吧？"
- 判断：数字不引用，只说「补贴 token」。

### C2. 投资人：模型公司缺垂直长程轨迹和环境，coding 强是因为优先级 — **keep**（新发现，现文没有）
- d2m07 王淮 [seg 1354–1362]："今天大模型的训练数据里，用于长程的垂直领域的，像 finance，甚至像 travel 里面的那些轨迹数据、那些环境，是远远不够的。今天大模型做得好的其实就一个领域，就是 coding。其他领域的智商水平，不是他们做不到，是不在 priority 上。"
- 判断：这是买方需求的直接证据：模型公司缺的就是垂直长程轨迹。也说明一旦优先级转向，垂直领域会被吸收（推断）。Copula 的金融、法律长程任务正对着这个缺口。

### C3. 投资人：医疗、金融、法律应用在 context、数据、部署上有壁垒；强数据垂类有复利 — **keep**（与 C2 放一起，说明卖家手里的筹码）
- d2m07 戴雨森 [seg 1197–1206]："我们在美国看到有很多在医疗、金融、法律这些领域的应用，相对大模型公司本身形成了自己在 context、数据或者部署上的壁垒。"
- d2m07 刘勇 [seg 1275–1283]："第二个是强数据相关的，我认为它是可以慢慢积累并且形成复利效应的……法律方面 Harvey 之类的都是非常好的。"

### C4. 投资人：应用公司在最新模型上套利，模型延伸到应用后空间收窄 — **merge → C1**
- d2m07 刘勇 [seg 1259–1266]："我认为他们是在最新模型基础上的套利……这种套利的空间随着模型延伸到应用的时候就减少了。"

### C5. MiniMax：harness 功能被训练进模型（plan mode、/goal） — **keep**
- d2m08 [seg 1552–1560]："plan mode 也不要了，没必要做 plan。为什么呢？因为我们的模型已经学会了 plan、execute and verify 这样的一个 loop。"
- d2m08 [seg 1561–1568]："那我们在 MiniMax 内部推演，觉得到后面可能会再被从 harness 当中去除的一个高频使用的功能是什么？就是 goal 这个命令。因为在我们模型训练的整个过程当中，我们要训练模型明白：我们要去完成这个任务，一直到能够把这个任务的最终结果交付到用户手上。"
- d2m08 [seg 1571–1585]："随着模型能力变得越来越强，它吸收的知识越来越多，它的强化学习做得越来越好之后，很多事情可能就没有必要了。"
- 判断：模型公司亲口说的吸收路径：外部工程手段 → 训练目标 → 从产品里删掉。

### C6. Tripo：coding agent 不用 Tripo 就能用代码搭出室内场景，公司改定位 — **keep**（新发现，现文没有）
- d2m10 [seg 1862–1884]："these indoor scenes were built entirely in code by agents, in tens of seconds, and no AI-native 3D model like Tripo was used. One of the researchers said, 'I haven't found an indoor scene that has to use Tripo.' Another colleague replied, 'Honestly, it was a bit of a panic.'"
- d2m10 [seg 1885–1894]："if you can describe it, an agent can write it; but if you can only recognize it, a model has to learn it. That's where we come in."
- 判断：被吸收的现场案例。3D 正是 Copula 在卖的数据品类（Blender 3D、Three.js、Godot）。（推断）专家数据商卖给模型公司的 3D 任务，加强的是通用 coding agent，挤压的是专业 3D 公司。两者是否有直接因果，原文没有证据。

### C7. 长程 benchmark 已包含操作 Blender、游戏引擎的任务 — **merge → A6**
- d1m20 [seg 2203–2206]，见 A6。

### C8. StepFun 把模型、开源 harness、托管执行打包卖 — **keep**（只作市场事实，弱化）
- d1m09 [seg 364–371]："Step 5 Preview提供理解任务、推理和选择行动的模型能力；Step Code实现agent harness……最后是我们最近发布的Studio，Studio会提供一些托管的执行体验，承载云端的harness和远端的工具。"
- 判断：d1m09 被标为宣传，只作「模型公司往上做 harness 和托管」的市场事实，不据此下结论。和 B7（自建 bench）合并成一句。

---

## D. 「自杀式」卖数据

### D1. 编码清晰的领域最先被吞；垂直 AI 的壁垒是把隐性知识自己编码 — **keep**（作为判断框架）
- d2m03 [seg 562–566]："为什么 AI 攻克数学和编程是最快的？因为这些都是编码非常清晰的领域……所以在编码的显性大陆上做应用，一定是又卷又贵的，而且一定会被 AGI 所吞没，因为编码越清晰，它往前推 frontier 就越容易。"
- d2m03 [seg 567–575]："如果你做的垂直领域 AI 要很难被 AGI 这些大公司吞没，最重要的是它在一个群岛的领域……有很多隐性知识没有被数据化。然后你能自己填海……编码就是填海：我把我这个行业数字化了，就是在填海。填海之后，这个东西就是我的壁垒。"
- 判断：讲者本人没谈卖数据。（推断）按她的框架，RL 数据就是把隐性知识编码成可验证任务和评分标准。卖给模型公司，就是把填好的海交给最强的解码器。

### D2. 台上有没有人在做自杀式卖数据 — 结论：**没有人承认**
- 卖数据的三家（Arena、You.com、Copula）主业都不靠被卖的那项能力本身：Arena 靠榜单（风险在公信力，见 A1），You.com 靠搜索调用（风险在调用量，见 A3），Copula 数据即主业。
- 握有垂直轨迹的公司（Harvey、Agoda、Cookiy）都自用，见 B 段。
- （推断）真正的自杀风险落在两类人身上：一是给 Copula 做兼职的行业专家，二是垂直应用公司。后者不卖也有风险：专家数据商可以直接雇行业从业者生产同领域任务（Copula 的金融、法律长程任务对着 Harvey 的领域），绕开应用公司本身。

### D3. 现文核心判断「应用公司产出的轨迹是它的筹码，也是被模型吸收的来源」 — **merge → D2，并修正**
- 修正：台上没有一家应用公司说在把轨迹卖给模型公司。现文这句把「可能」写成了「正在发生」。改为：应用公司都在自用，供给来自专家数据商和平台。

---

## E. 现文其他内容

### E1. 现文「数据供给方在变多」— **drop**
- 原因：三家卖家不构成「变多」的趋势证据，无时间对比。

### E2. 现文「You.com 帮 NVIDIA 做后训练」— **keep，改写**
- d1m05 [seg 875–883]："David will take us through a case study where we helped CoreWeave and NVIDIA post-train the Nemotron model."
- 判断：保留，但只作 A2 的背景，不单独成点。
