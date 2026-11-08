# S5 数据 Infra：证据表

核实范围：`data/03_clean/*.md` 全部 53 场转录。用 summaries 初筛后，对 trace / 轨迹 / snapshot / 快照 / checkpoint / fork / replay / 回放 / sandbox / 沙箱 / 对象存储 / S3 / lake / 湖 / cache / 缓存 / 飞轮 / 回流 / 闭环 / 标注 / 质检 / acquir / 收购 / Elastic / Deepgram / ClickHouse 做了中英文 grep，再通读相关段落。

宣传标记（substance_filter = no）：d1m15 Zilliz、d2m18 LanceDB、d1m19 Google、d1m17 TiDB、d1m12 Daytona、d1m06 Baseten。这些只当市场事实用（谁在卖什么、说自己解决什么问题），不在它们的说法上建立洞察。

---

## A. 现有表格逐条核实

### A1. Zilliz：数据量每年涨一个量级，固定容量扛不住 → 对象存储底座、热温冷分层
- d1m15 [seg 1484–1488]："今年已经到了千亿级……去年是百亿，前年是 10 亿。每一年都如此……每年翻一个数量级。"
- d1m15 [seg 1542–1551]："本质上来讲，如果拿数据库架构去承载指数级的 AI 数据增长，它是一个拿有限容量、有限资源去对抗指数增长数据的问题，两者是不匹配的。"
- d1m15 [seg 1558–1566]："其实是三层……服务器本地的 local cache……远端缓存 remote cache；最底下是对象存储……热、温、冷三层"
- **判定：merge → C2（留存）**，只作市场事实。增长数字是 ASR 数字，又出自宣传场，删掉。"对象存储底座 + 分层"保留为"存储厂商在卖什么"。

### A2. LanceDB：每换一次模型就要重算历史数据；说不清训练用了哪版数据 → 列级增量、cell 级脏标记、snapshot
- d2m18 [seg 3294–3303]："研究员会问：我们现在这个模型，它上一次训练，到底是基于哪一版的 caption？……每一次有了新的数据……每一列全都要进行补算；或者……决定采用一个新的 embedding API……它的每一个数据时刻都在变。"
- d2m18 [seg 3304–3309]："这个数据，从它的源头……只会采集一次。在后续不断的演进中，它会不断地需要进行重建……每一次的模型和更新，都是一次对历史数据的重新构建。"
- d2m18 [seg 3374–3383]："把一个表是用哪个模型去训练的、在什么时候训练完成的，包括一些用户自己的 metadata，全都加到这个 snapshot 里面。"
- **判定：拆开 merge**。"只采一次、反复重建" → C2（留存）；"说不清用了哪版数据 / snapshot" → C3（重放）。宣传场，只写成"LanceDB 说研究员遇到的问题是…"。

### A3. Langfuse：轨迹太大人读不完、塞不进上下文 → 摘要、聚类、只回传最严重失败；后台 agent 跑改进循环
- d1m03 [seg 562–567]："no one can actually read all traces by hand anymore."
- d1m03 [seg 578–585]："an agent's context usually doesn't fit millions of traces……So you need to shape your data first."
- d1m03 [seg 586–600]："You take traces and summarize them as trajectories……use smaller, less expensive language models to summarize these trajectories along dimensions that you care about……embed them, and cluster them……look only at the failures that are most egregious, and then pass the full traces for these failures back to your model."
- d1m03 [seg 601–607]："teams will use background agents……long-running, find failures, propose fixes, and backtest these changes"
- **判定：keep → C4（回流）**。非宣传场，做法具体。

### A4. Google：RL 中基础设施故障被记成任务失败，污染训练数据 → 预热池、镜像缓存，首条指令亚秒级
- d1m19 [seg 2125–2131]："这些情况有可能被 reward 评估为这个任务没有完成，比如内存溢出或者超时等等。这样你整体的训练数据其实就被污染了……这会影响到最终模型的权重输出。"
- d1m19 [seg 2150–2159]：预热池、镜像就近放置与 cache、控制平面优化。
- **判定：merge → C4（回流）**，只写成"Google 说它要解决的问题"。"亚秒级"是数字，删掉。

### A5. 结论句："这一层的厂商都在改卖点：让 agent 轨迹和训练数据能被反复重算"
- 支持：d2m18 [seg 3304–3309]（反复重建），d1m17 [seg 1930–1934]（checkpoint + fork 重跑），d1m15 [seg 1596–1604]（离线挖掘 trace 回到 harness / post-training）。
- **判定：merge 进主结论**。方向对，但只说了厂商卖点。非宣传场（d2m19、d2m17、d1b02、d1m16）也有同样的需求，主结论要建在这些上面。

### A6. 收购："Langfuse 归 ClickHouse，Jina 归 Elastic，Pipecat 归 Deepgram"，"单点工具在被有数据底座的公司收购"
- Langfuse → ClickHouse：**原话证实**。d1m03 [seg 423–431]："I'm one of the co-founders of Langfuse, which was acquired by ClickHouse, the real-time database company, at the start of the year."
- Jina → Elastic：**转录正文里没说**。只出现在议程机构名 "Jina AI by Elastic"（01_talks.csv、d2m20 front matter），演讲正文没提 Elastic，也没提收购。
- Pipecat → Deepgram：**转录正文里没说收购**。只有 front matter "Daily.co (Pipecat; now part of Deepgram)"，加上讲者一句 d2m05 [seg 919–926]："Pipecat, which is the open source library I work on……I'm at Deepgram"。而且 Deepgram 是语音模型公司，算不上"数据底座"，d2m05 讲的也是语音 agent 评测，不在本节范围。
- **判定：drop 这句概括**（一条原话证实、一条只有机构名、一条错归类，撑不起"在被收购"这个规律）。保留 Langfuse→ClickHouse 这一个事实，放进 C2，作为"存储公司把 trace 当成自己的负载"的例子。

---

## B. 现有文本漏掉的候选点

### B1. Optiver：LLM 请求有状态，failover 和协议翻译静默破坏缓存与 thinking block（推理服务）
- d1m16 [seg 1664–1669]："HTTP 200, the standard HTTP code for successful requests, does not always mean success here……a request that started streaming nicely and suddenly stalled halfway"
- d1m16 [seg 1675–1685]："the response was silently dropping these thinking blocks……you don't see it in the gateway……So in the end: increased latency and increased cost……it was actually a bug in translating the protocol from Anthropic to OpenAI"
- d1m16 [seg 1695–1708]："you cannot simply load balance between them, because the nature of an LLM request is stateful."
- d1m16 [seg 1719–1732]："if you simply split your traffic between two providers, even if they serve the same model, you can easily break your cache……make sure that a single session from a single user always hits one model"
- d1m16 [seg 1746–1753]："keep your fallback in exercise……we always split 10% of the traffic, or sessions, to the secondary model provider."（比例是数字，不引）
- d1m16 [seg 1853–1858]："We are leaning more towards protocol-independent harnesses — harnesses that can speak multiple protocols, rather than translating between them."
- **判定：keep → C1（运行时状态）**。非宣传场，生产经验，做法具体，不是常识。

### B2. Optiver：合规 prompt 日志写进 Postgres 拖垮网关 → 各区域直写 S3
- d1m16 [seg 1768–1773]："our compliance requirements ask us to keep track of all the prompt logs……we chose to just flip a switch in this open-source gateway to say 'store this in Postgres'."
- d1m16 [seg 1774–1793]："massive amounts of data being sent across the Atlantic……authentication latency……We send it to S3 object storage instead, directly from each region."
- **判定：keep → C2（留存）**。这是 C2 里唯一来自使用方（非存储厂商）的"日志该进对象存储"证据。

### B3. Optiver / Manus：trace 的读者变成了 agent
- d1m16 [seg 1812–1829]："Metrics help you understand overall gateway health……Logs help you answer compliance questions……But one thing we were missing was tracing."
- d1m16 [seg 1830–1839]："one tool call was taking more than three minutes. That's why the prompt was slow. Without the trace, it would have been very difficult for us to tell."
- d1m13 [seg 1054–1061]："全链路的otel日志追踪系统，这是加速AI debug的一个关键。因为AI可以用同一个trace ID一路查到底，最后可以直接定位到这个bug是由哪个仓库、哪个代码、是谁在哪一次改动引起的。"
- d1m03 [seg 568–577]："It's important that you're able to connect all of your application data, your traces, to coding agents via MCP, API, or CLI."
- **判定：merge → C4（回流）**。"要上 tracing"本身是常识，删掉；"trace 要接给 agent 读"（d1m13、d1m03）并进 C4。

### B4. MiniMax：动态 MCP 工具列表和长前台命令破坏前缀缓存
- d2m08 [seg 1618–1631]："MCP 有个问题，就是它在 agent 的运行过程当中是动态加载的……你的工具列表可能会产生变化……那你的前缀缓存是没有办法严格保证的。这样的话，你的 agent 跑起来可能就会变得非常贵。……把所有这样的 MCP 工具全都放到了一个 connector 的 CLI 里面去，通过在这个 CLI 里面做渐进式披露的方式"
- d2m08 [seg 1654–1662]："安装依赖就要超过 5 分钟……你怎么样能保证你的前缀缓存？那就要用到后台任务，把它转到后台。"
- **判定：keep → C1**，和 B1 合成一条"缓存会被看起来无害的改动打破"。harness 层的细节可能在别的章节出现，这里只用一句。

### B5. Techcombank：成本核心指标是缓存之后的有效混合单价；provisioned 为主、按 token 兜底
- d1m18 [seg 1967–1972]："it all boiled down to one single metric……the effective blended cost per million tokens. It is basically the cost of input and output of the whole organization, after the caching rate."
- d1m18 [seg 2043–2048]："it's best to keep pay-per-token as a fallback rather than removing it completely……GLM provisioned as the main model and GLM pay-per-token as the fallback."
- d1m18 [seg 2003–2010]：盈亏点公式（GPU 租金 ÷ 有效单价）。
- **判定：盈亏点公式 drop（就是租和买的盈亏平衡，属常识）。"指标算在缓存之后" merge → C1**，作为"缓存直接决定账单"的使用方证据。

### B6. Harvey：本地 agent 的 thinking trace 会丢，搬到云端才变成可收集的数据
- d1b02 [seg 226–232]："大家在本地跑的这些 Agent，最后 Agent 的 context、thinking traces 都不见了。但一旦我们有了这么一个大家都可以协作的 Agent，这就成了我们可以在线上收集的数据，并且是内部数据"
- **判定：keep → C1**（运行环境决定状态留不留得住）。

### B7. Harvey：重放评测时后来的信号会泄露进去，收集的数据大多不能用
- d1b02 [seg 223–225]："因为 harness 和模型都是可以替换的，所以一个 task 从最开始到最结束，这个固定的流程都是可以重放的。这个固定流程就变成了我们的一个 evaluation case"
- d1b02 [seg 289–295]："我们发现收集了那么多数据，真正能用的并不多……如果你要把它重放一遍，有可能这个 code review 本身有另外的人或者 Agent 在上面留了更多的 code review，那你重放的过程中，这个 Agent 可能会受到后来那些 signal 的影响，它就不是一个很好的 case。或者这个 PR 之后有人又加了新的 change……所以我发现花更多时间的是研究这个评测集该怎么选出来。"
- **判定：keep → C3（重放）**。这是本节最有价值的使用方证据：重放要冻结的是当时的现场，后来的状态会污染样本。

### B8. Agoda：把 merged MR 回放成自家基准，用它训练 agent
- d1b07 [seg 893–896]："we get our ticket and GitLab description and generate a prompt. Second, we ask the agent to replay. And the last step is that we evaluate our results against the golden tests that we already have in the merged MR."
- d1b07 [seg 919–924]："you should start to use your merged MRs to train your agent."
- **判定：merge → C3**，作为"历史记录 = 可重放数据"的第二个使用方例子。"信自己的评测"属于评测章节，这里不展开。

### B9. TiDB：重跑结果不可比 → meta 快照、events 和文件系统 checkpoint 绑定，从同一现场 fork
- d1m17 [seg 1930]："如果我们每次都从头重新跑，输入、工具返回、文件可能就发生了变化，结果就会有差异，这个变化到底来自策略还是来自现场的变化，就很难解释了。"
- d1m17 [seg 1931–1934]："把已经保存的 meta 快照和 events，与文件系统保存文件的 checkpoint 绑定……从文件系统里面 fork 出一个当时一模一样的文件内容"
- **判定：merge → C3**，宣传场，作市场事实（存储厂商在卖"还原现场"）。

### B10. TiDB：sandbox 回收后文件丢失 → 独立于 sandbox 的持久文件系统
- d1m17 [seg 1887–1890]："一般任务结束后，我们就会回收 sandbox，同时清理策略也会把对应的 EBS 清理掉。这种情况下，虽然 meta 记住了很多东西，但是我们的文件都丢了。"
- d1m17 [seg 1894–1895]："session A 写完之后，就可以把 sandbox 释放掉，session B 可以 mount 同样的文件系统"
- **判定：merge → C1**，市场事实。

### B11. TiDB：只看任务成败解释不了成本，要按工具 / 任务类型批量分析 trace
- d1m17 [seg 1920–1924]："如果我们只看最后这个任务成功或失败，解释不了我们的成本花在哪里，因为 agent 可能在不断地重试……只有一批 trace 才能帮助团队决定后面的优化方向。我们可以按工具、按任务类型来看重试、耗时、调用量，再关联验收结果，算出成功率以及包含失败重试的单位成本"
- d1m17 [seg 1925–1929]："原始的 trace 我们可以持续加载，然后用 SQL 去展开 JSON、提取字段……最后在 TiDB Cloud 的 Lake 这个产品上、在对象存储上做保存。"
- **判定：分析方法 drop**（宣传场；和 A3 Langfuse 的批量分析重复；"批量看 trace"本身也不新）。**"trace 存在对象存储上的 Lake" merge → C2**，市场事实。

### B12. Daytona：K8s 为无状态长驻服务设计，agent 要有状态、短命的沙箱
- d1m12 [seg 876–885]："It's ideal for running long-running, stateless web services. But with agents, the requirements are completely opposite. Agents need, number one, statefulness……And most of the tasks agents do are short-lived"
- d1m12 [seg 929–939]："if you want to achieve statefulness on Kubernetes, you have to mount some kind of external storage. And this is the trap, because once you do that, all of your file system operations go over the network"
- **判定：merge → C1**，市场事实。

### B13. Google 与 Daytona 对 K8s 的说法相反
- d1m19 [seg 2180–2184]："如果你是一个大规模实验室，在百万量级，或者是比它更小的实验，大部分情况下，我们目前的方案，叫 agent sandbox，基于 Kubernetes，已经能够满足你的需求。"
- 对照 d1m12 [seg 836–843]："choosing Kubernetes for the agentic infra layer is not a good option"
- **判定：keep → C1，写成一句备注**。两家都是宣传场，这条只说明沙箱层还没有共识，卖家说法互相矛盾。

### B14. Nowledge：不知道哪些知识以后有用，所以全部轨迹完整存下
- d2m19 [seg 3443–3457]："你不太能真的知道在 6 个月之后，还有哪些被升华过、被蒸馏的知识值得被再记录。所以我们最终的实践，简单来说就是，在我们最早版本的系统里就决定把所有的 trace trajectory 作为 episodic memory 完全地存储。然后……用一个小模型、用很简单的定制 prompt 去做 triage。"
- **判定：keep → C2（留存）**。非宣传场，给出了"先存后定"的理由。

### B15. 未来不远：执行过的、失败的、想象过没执行的轨迹都存下，作为下一代训练养料
- d2m17 [seg 3166–3172]："我们如何把已经执行过的动作，甚至想象过但没有执行过的动作保存下来……这些数据就可以用作下一代模型的训练。所以自进化机制的核心是：不要人为参与来决策模型什么时候进步、什么时候更新，而是由一个统一的闭环数据来源"
- d2m17 [seg 3193–3205]："失败的数据也可以拿来训练……候选轨迹仍然可以被保存下来做训练。"
- **判定：keep → C2**。机器人领域独立给出同一结论：失败和未执行的轨迹也要留。

### B16. 穹彻：数采走出工厂后，data infra 要近乎实时反馈给采集员；人工质检标注完全放弃
- d2m14 [seg 2722–2729]："数据采集离开固定的数采工位、进入真实的生产和工作场景后，管理的困难极度加大，因为这些人可能主观上偷懒，或者客观上不理解数据采集的过程……当数据足够多样……质检和标注的难度也会急剧上升。"
- d2m14 [seg 2730–2739]："数据不只要交付给训练，还需要在几乎 T+0 的时间范围内给一线数采团队第一时间的反馈……至少在穹彻今天的实践里，我们已经完全放弃了生产级别的人工质检、标注……我们认为至少在具身这样的场景里，人类标注员不具备实践的价值。"
- **判定：keep → C4（回流）**。非宣传场，结论强，现有文本漏了"训练数据管理"里最硬的一条。

### B17. Arena：用 LLM judge 加人工从 trace 抽信号；把 trace 转成 rubric 和 RL 环境卖给实验室
- d1m07 [seg 1176–1177]："We leverage a combination of LLM judges and careful human curation to extract the signals from each trace"
- d1m07 [seg 1189]："Arena is also working on turning some of the agent traces into rubrics and RL environments to help labs with post-training."
- **判定：keep → C4**。trace → RL 环境的第二个独立来源。

### B18. Langfuse：改进循环产出的标签被拿来造 RL 环境、训练自己的开源模型
- d1m03 [seg 624–628]："the next step that we see the best teams starting to take right now is to build their own reinforcement learning environments, because the labels you get from running the improvement loop are signals you can use to build tasks, build verifiers, and in the end train your own open-source models"
- **判定：keep → C4**。这是可观测和训练两条线的接口：观测平台说它的数据终点是 RL。

### B19. You.com：RL 数据集比 tooling / environment 更重要；去污染；按难度过滤
- d1m05 [seg 974–980]："最重要的其实是你的RL data set。这个RL data set在你做后训练的时候，其实比tooling或者environment更重要。"
- d1m05 [seg 1015–1020]："做decontamination：你做RL的时候，不想你的data set里面有这些RL benchmark的答案"
- d1m05 [seg 1021–1031]：pass@8 过滤，太难或太简单的题都丢掉。
- **判定：merge → C4，写成一句备注**（和 Google"卡在沙箱调度"的说法对照）。具体配方属于后训练章节。

### B20. 展商：RL 环境 / 专家数据，以及可恢复的 agent 存储
- exhibitors.csv：Copula Lab（"专家数据、RL 环境、benchmark"），MindLab（"benchmark、数据开发、后训练"），Tonbo（"开源嵌入式数据库，面向 serverless、数据密集型 agent 负载"；展台 demo "yield your agentic workload on your laptop and resume it anywhere"）。
- **判定：keep，标 展商**。Copula/MindLab → C4；Tonbo → C1。

### B21. 投资人：除 coding 外，长程垂直领域的轨迹数据和环境远远不够
- d2m07 [seg 1354–1362]："今天大模型的训练数据里，用于长程的垂直领域的，像 finance，甚至像 travel 里面的那些轨迹数据、那些环境，是远远不够的。今天大模型做得好的其实就一个领域，就是 coding。"
- **判定：drop**。只是观点，没有证据；对本节的 infra 问题帮助不大。

### B22. Zilliz：离线挖掘做得不好的 trace，回到 harness 或 post-training；按查询只加载涉及的分片
- d1m15 [seg 1596–1604]："要去找哪些 agent trace 也好、数据本身也好，是我的模型或者 agent 做得还不够好的，把这些挑出来之后，加到我的 harness 的部分，或者 post-training 的部分……只有这次查询一定涉及的那一部分数据会加载到上面来，随着任务结束或者请求结束之后，上层又回到零负载。"
- **判定：merge → C2**，市场事实（存储厂商把 trace 挖掘列为目标负载）。

### B23. Zilliz 转述的 Cursor 故事（几个月换四套数据库）
- d1m15 [seg 1518–1527]
- **判定：drop**。二手转述，来源是 YouTube 讲座和媒体标题，原话也没核实过。

### B24. Baseten：推理技术罗列（PD 分离、量化、投机解码、KV cache 感知路由）
- d1m06 [seg 1155–1157]
- **判定：drop**。宣传场，内容是公开常识。

### B25. Jina：匿名访问比例上升，agent 读网页的 token 成本高于广告收入
- d2m20 [seg 3752–3759]："匿名访问的比例已经从半年之前的 20% 提高到现在的 36.9%。如果这个趋势继续的话，我们服务的免费部分可能就会受到影响。"
- d2m20 [seg 3736–3746]：网页直接进模型的单价和每千次浏览广告收入的对比。
- **判定：drop（不在本节范围）**。这是 agent 访问网络的经济问题，属于搜索 / 数据接入章节。数字也不能引。

### B26. 企业语义层 / 上下文层（DataHub、Datus、HICAP 的口径追溯）
- d1b08、d1b10、d2m04
- **判定：drop（不在本节范围）**。属于企业上下文 / 语义层章节。

### B27. Google：沙箱大部分时间空着等模型生成，GPU 也跟着等
- d1m19 [seg 2132–2137]："80% 的时间它都是空的……80% 的时间是在等模型产生……非常昂贵的 GPU……就在那儿等几分钟"
- **判定：drop**。宣传场，带数字；也和 C4 的主线（数据质量）无关。

---

## C. 归并后的支撑点（对应 s5_revised.md）

- **C1 运行时状态**：B1、B4、B5（缓存指标）、B6、B10、B12、B13、B20（Tonbo）
- **C2 全量留存，以后再算**：B14、B15、B2、A2（重建）、A1、B22、B11（TiDB Lake）、A6（Langfuse→ClickHouse）
- **C3 重放要冻结当时的现场**：B7、B8、A2（snapshot）、B9
- **C4 回流的筛选交给模型，终点是 RL 环境**：A3、B18、B17、B16、A4、B3（trace 接给 agent）、B19、B20（Copula / MindLab）

主结论的依据：C1–C4 每条都至少有一个非宣传场的使用方证据（d1m16、d1b02、d2m19、d2m17、d1b07、d1m03、d1m07、d2m14）。存储和沙箱厂商（d1m15、d2m18、d1m17、d1m12、d1m19）卖的东西正好对上这四个需求，但只作为市场事实引用。
