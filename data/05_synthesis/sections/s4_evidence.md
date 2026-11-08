# s4 证据表：Agent Infra 在解决什么问题

谁需要读：核对 s4_revised.md 每条说法出处的人。只看结论的读者直接读 s4_revised.md。

范围：框架与治理（平台、框架、模型网关、身份与权限）、外部连接（搜索与数据 API、企业知识与本体、支付与交易）、运行底座（沙箱、存储）。

检索方式：先用 all_talks.json 圈出 d1m02、d1m03、d1m05、d1m09、d1m12、d1m14、d1m16、d1m17、d1m18、d1m19、d1b02、d1b03、d1b04、d1b08、d1b10、d2m04、d2m08、d2m12、d2m16、d2m19、d2m20；再对全部 53 篇转录 grep sandbox/沙箱、gateway/网关、permission/权限、identity/身份、支付/payment、credential/凭证、MCP、ontology/本体、语义/口径、audit/审计、snapshot/快照、container、browser/浏览器、search/搜索、云端 等词，读命中段落全文。

标注：〔PR〕= substance_filter.csv 判为以宣传为主的演讲，只作市场事实（谁卖什么、说自己解决什么问题），不作为洞见依据。展商 = exhibitors.csv。

---

## A. 框架与治理

### A1. LLM 请求有状态，网关不能当普通 web proxy 用 —— keep

d1m16 Optiver（自建，非 PR）

- "one tricky thing about an LLM gateway, compared with a typical web proxy, is that HTTP 200, the standard HTTP code for successful requests, does not always mean success here. ... You can have a request that started streaming nicely and suddenly stalled halfway" [seg 1664–1669]
- "you cannot simply load balance between them, because the nature of an LLM request is stateful. ... If the user hasn't seen the response yet ... you can try the second provider ... But in case streaming has already started ... we have no choice but to surface the error to the user." [seg 1695–1708]
- "if you simply split your traffic between two providers, even if they serve the same model, you can easily break your cache." [seg 1719–1727]
- "make sure that a single session from a single user always hits one model ... never one session across the two models." [seg 1728–1732]
- "if a feature doesn't work on both providers, just disable it, and have a common feature set for users to use." [seg 1733–1745]
- "We shouldn't start sending requests to the fallback only when the primary fails; we should keep exercising it even when everything is working fine." [seg 1746–1753]

判断：keep。核心事实是"LLM 请求有状态"，由此推出四条做法：首个 token 之前才能切换供应商、会话粘滞、两家供应商只开共同功能、备用通道平时就分流。来源是自建方的运维经验，不是卖点。

### A2. 协议翻译造成静默失败：丢 thinking、破缓存 —— keep（并入 A1 同一行）

d1m16 Optiver

- "Because we are doing protocol translation, we have seen broken cache in the middle. ... if your cache is broken because something is wrong in the middle, you can see from the cost that it doubles, triples, quickly." [seg 1670–1674]
- "the response was silently dropping these thinking blocks. ... you don't see it in the gateway. ... it was actually a bug in translating the protocol from Anthropic to OpenAI" [seg 1675–1685]
- "protocol translation is hard. We are leaning more towards protocol-independent harnesses — harnesses that can speak multiple protocols, rather than translating between them." [seg 1853–1858]
- "we decided to build our own gateway, based on a much leaner feature set ... It's not something that everyone should do." [seg 1840–1852]

判断：keep，与 A1 合并。现有文本已有这一行，核实无误。补充：这类故障不进监控，最先是在成本上看出来，thinking 丢失是用户自己的 agent 发现的。

### A3. 缓存命中是网关和 harness 共同的成本约束 —— keep（新增，现有文本缺）

- d1m16："You should have a nice, high cache rate, which basically equals saving money for you" [seg 1670–1674]
- d2m08 MiniMax（非 PR）："MCP 有个问题，就是它在 agent 的运行过程当中是动态加载的 ... 你的前缀缓存是没有办法严格保证的。这样的话，你的 agent 跑起来可能就会变得非常贵。所以我们做的一件事情叫做 discovery inside a tool call：我们把所有这样的 MCP 工具全都放到了一个 connector 的 CLI 里面去，通过在这个 CLI 里面做渐进式披露的方式" [seg 1618–1631]
- d2m08："安装依赖就要超过 5 分钟，甚至要十几分钟。在这样的情况下，你怎么样能保证你的前缀缓存？那就要用到后台任务，把它转到后台。" [seg 1654–1662]
- d1m18 Techcombank（非 PR）："it all boiled down to one single metric ... the effective blended cost per million tokens. It is basically the cost of input and output of the whole organization, after the caching rate." [seg 1967–1972]

判断：keep。三家非 PR 来源各自在网关（供应商切换、协议翻译）、harness（工具列表、长命令）、组织成本指标上碰到缓存。写进 revised 作为网关一行的"跟踪指标"，不单列成观点，避免和 s2 的 harness 内容重叠。

### A4. 自建算力与按 token 付费混用，网关负责兜底 —— merge（并入 A1 网关行）

d1m18 Techcombank

- "it's best to keep pay-per-token as a fallback rather than removing it completely. In our setup, Databricks provides Unity AI Gateway ... we can set up GLM provisioned as the main model and GLM pay-per-token as the fallback." [seg 2043–2048]
- 盈亏点公式：分子是 provisioned GPU 成本，分母是按 token 付费的单价 [seg 1982–1984]

判断：merge 到 A1。现有文本把"公有和私有模型混用"归给 Optiver，属于错配：Optiver 讲的是多家公有供应商互备；公私混用的自建方案例是 Techcombank。盈亏点计算本身属于推理成本话题，s4 不展开。

### A5. 跨区域：全局身份、本地推理 —— merge（并入 A1，revised 只留一句或不写）

d1m16

- "our compliance requirements ask us to keep track of all the prompt logs ... massive amounts of data being sent across the Atlantic ... authentication latency ... It's two seconds." [seg 1768–1783]
- "we immediately turned off prompt logging in the database ... We send it to S3 object storage instead, directly from each region. ... we moved all authentication local by creating local replicas." [seg 1784–1793]
- "our gateway has global identity — a single key works everywhere — but inference stays local. We have no remote dependencies on the inference hot path. ... On this part we chose eventual consistency." [seg 1794–1803]

判断：merge。价值在"鉴权、计费、合规日志都不能挡在推理热路径上"，revised 用半句带过。

### A6. 全链路 tracing 才能定位"慢" —— merge（并入 A1）

d1m16："we found from this trace that one tool call was taking more than three minutes. That's why the prompt was slow." [seg 1830–1839]

判断：merge。tracing 本身是常识；有价值的是用户感知的"推理慢"实际出在工具调用。

### A7. 企业统一网关管公私模型的预算与审计 —— merge（展商事实，并入 A1）

展商 Raytone："企业 token 全生命周期平台：统一调用公私有模型、预算与审计网关、agent 工厂"。

判断：merge，作为"已有商业产品"的市场事实，标展商。

### A8. agent 冒用人的身份会继承人的全部权限，harness 的权限开关挡不住 —— keep

d1m02 Microsoft（非 PR）

- "It's dangerous to have an agent impersonate you, because that agent inherits your security context. That agent can do everything that you can do." [seg 213–228]
- "Most harnesses will have some kind of permission system ... they are optional." [seg 229–238]
- "it might try to do file access, or a file delete, and find that it can't do that here. But then it would say, 'Oh, wait, but I got shell scripts.' So `rm -rf` ... Or then maybe I turn off shell scripts, and then the agent is like, '... I'm a coding agent. I can write a Python program and delete all the files.'" [seg 239–254]
- "these agents with their own identities — run in their own security context. ... I gave it `Files.Read.All`. ... This is the principle of least privilege as applied to agents." [seg 272–284]
- "There's nothing that it can do to delete a file, because its user just can't do that." [seg 285–297]

判断：keep。现有文本已有，核实准确。要点是限权放在身份层，harness 开关只是建议。

### A9. 每次工具调用前判断"这次调用是否符合用户任务" —— keep

d2m16 1Password（非 PR）

- "the user's task is to investigate a failing service, and the proposed tool call ended up being a modification to the production account. And the agent's reasoning isn't necessarily trustworthy." [seg 3004–3010]
- "It needs to be able to execute with low latency at runtime ... And ideally it should run locally, so that the context, including sensitive information, doesn't go off-host." [seg 3011–3015]
- 对比方案：规则（regex）、托管大模型（上下文离开本机、慢、贵）、自训分类器（要大量标注、工具调用数据一变就要重训）[seg 3016–3026]
- "we need to be careful not to choose a single threshold across all models, because sometimes that threshold can be too high for one, and you end up deferring way too many calls to people" [seg 3062–3066]
- "The tool calls can be intercepted by a gateway implemented as an MCP server. ... invoke a policy gate component ... to make a decision to either approve, deny, or escalate the tool call" [seg 3067–3077]
- 跟踪指标："how many risky calls we are letting through ... how many safe calls we are letting through" [seg 3087–3093]

判断：keep。与 A8 互补：A8 限定 agent 最多能做什么，A9 判断这一次该不该做。现有文本把两者写成同一行"做法"，revised 拆开说明各管哪一段。

### A10. 数百上千个 agent 后的变更管理、审计、第三方 agent 治理 —— drop

d1b03 Dify〔PR〕

- "out of their thousands of agents, they don't have a view on which one uses what knowledge base." [seg 421–427]
- "you just have to be able to govern all of them. No customer is going to accept a governance strategy that only covers 80% of the risk areas." [seg 499–510]

d1m02 Microsoft 只演示了 Agent 365 控制台里由管理员按模板给一类 agent 设权限 [seg 255–262, 285–297]，没有讲"数百个 agent 的影响面"。

判断：drop。Dify 是 PR 演讲，"规模上来要管"属于常识；现有文本把 Microsoft 并列为这一行的公司属于错配，Microsoft 的控制台内容已归入 A8。

### A11. agent 从本地转到云端，上下文和轨迹得以保留 —— merge（并入 C4 存储）

- d1b02 Harvey（非 PR）："大家在本地跑的这些 Agent，最后 Agent 的 context、thinking traces 都不见了。但一旦我们有了这么一个大家都可以协作的 Agent，这就成了我们可以在线上收集的数据" [seg 226–232]
- d1m09 StepFun〔PR〕："交给云端的工作，在本地客户端断开以后，仍然可以持续推进。" [seg 439–445]

判断：merge 到 C4。Harvey 的协作和评测部分属于 s2，这里只取"本地 agent 不留状态"这一事实。

---

## B. 外部连接

### B1. 网站和风控把 agent 当成异常：被拦截、被判盗刷、被平台屏蔽 —— keep（新增，现有文本只写了"支付风控会拦截"）

d1b04 Visa〔PR，但以下是 Visa 描述的市场现状〕

- "比如大家知道 Cloudflare，你到一个网站以后，它可能上来先问你是不是个 bot。如果我的 agent 去的话，它肯定诚实地说我是个 bot，那你连网站的页面都 retrieve 不了，就被 block 了" [seg 635–646]
- "大半夜我们的银行突然收到好多笔一分钱、两分钱的交易，在传统的信用卡风控模型里面，这肯定是被盗了 ... 很多以前的风控规则是要改的" [seg 647–655]
- "前两天 Muse 发布的时候，Amazon 就把 Muse 给 block 了，然后前两天好像 Grok Bot 也被 Amazon block 了。" [seg 548–559]

d2m12 masons.ai〔PR〕

- "What if you want to take an action to change the state in other people's environment? Will other people allow you to do so? Think about why Amazon banned Muse recently." [seg 2279–2298]
- "not many brands wanted to join this structure of ecosystem, because they don't want to be white-labeled fulfillment. They don't want to be reduced to an API." [seg 2357–2366]

判断：keep。两场独立演讲都提到 Amazon 屏蔽 Muse。作为市场事实使用，不采信 Visa、masons 对自家方案的判断。

### B2. agent 读网页侵蚀免费服务和广告模式，按次付费未必走得通 —— keep（新增，现有文本缺）

d2m20 Jina（非 PR）

- "我们服务有一个特点：它提供一定的 free quota，不仅是免费访问，而且是匿名访问，这样就允许 AI agent 自己来访问我们的服务。" [seg 3696–3701]
- "从 Reader 后台看，匿名访问的比例已经从半年之前的 20% 提高到现在的 36.9%。如果这个趋势继续的话，我们服务的免费部分可能就会受到影响。" [seg 3752–3759]（数字为语音识别，revised 不引用，只写他跟踪的指标是"匿名访问占比"）
- "如果你直接把网页的全部内容放到主流模型里面去处理，这个单价是非常惊人的 ... 作为对比，互联网广告每千次网页浏览的收入大概是三到十五刀。" [seg 3736–3746]
- "各个网站做反爬的出发点可能不一样：大站主要是想保护数据，而小站，像我们 Reader，主要是想节省 IT 资源。当然还有一条暗线，就是互联网网站基于广告的这样一种商业模式。" [seg 3760–3766]
- "我觉得渠道并不是问题，价格才是问题，而价格是不可能低的 ... 如果以发达国家的网页定价来看，全球南方国家 ... 是很难跟上的 ... "给钱就能抓"也并不会真正实现 ... 很难防止数据倒卖。" [seg 3775–3786]
- "唯一一件我可以同意的事情是，控制 Agent 网页访问这件事务必要发生在网关这一层 ... 前四个机构已经占比超过 50%。这意味着，如果几家大的机构能够达成一致，那么行业的格局是有可能被改变的。" [seg 3787–3794]
- "我们给 Agent 一段广告语，让 Agent 复述一下核心口播 ... 也可以运用一些可以验证的任务，就像之前的 reCAPTCHA 一样" [seg 3795–3809]

判断：keep。这是外部连接层唯一一场非 PR、且直接谈"内容方和 agent 谁付钱"的演讲，和内容行业关系最近。和 B3 形成对照：支付方在铺按次付费的通道，提供网页读取的 Jina 不看好按次付费。

### B3. agent 替人付钱：凭证、授权、agent 与商户互认 —— keep（市场事实）

d1b04 Visa〔PR〕

- "我今天是不可能直接给 agent 发一张卡的 ... 一个是 tokenize，就是你不会把卡号直接给到智能体；另外，它可能是一个 scoped token，比如它可能今天晚上就失效了，它的上限是多少，这些都是可以控制的。" [seg 660–666]
- "这个 token 拿去消费的时候，一定要匹配用户的意图和他的授权，而且在这个阶段是要明确授权的。" [seg 667–671]
- "智能体跟商户之间实际上要有一个 mapping ... Trusted Agent Protocol。在这里面，一是我们会对 agent 进行认证，二是商户需要有一个 tunnel 能够跟 agent 进行握手" [seg 672–678]
- "这个分你可以想象成当年的 PageRank：PageRank 衡量的是 relevance，而这个分衡量的是你的 usability，包括 agent 到你这来容不容易下单。" [seg 679–685]
- "买超是不会的，因为我们会做限额；但它如果买错了，或者产生一些纠纷的时候怎么办？" [seg 607–615]
- 行业协议：Google 的 UCP、Stripe、Shopify、Visa；Machine Payments Protocol [seg 566–570, 600–606]

展商：Stripe（支付与 AI 产品定价）、Adyen（支付）、Clink（面向人和 agent 的全球支付与订阅计费）。

判断：keep，作为市场事实。scoped token 与 A8、A9 结构相同，用于 revised 末尾的规律。商户"agent 可用性评分"对内容行业有参照意义，但只有 Visa 一个来源，revised 只写一句。

### B4. 企业口径不统一，模型越强错得越自信 —— keep（新增，现有文本缺）

d2m04 HICAP（非 PR）

- "更难的是口径是否统一："交付"这个词，在营销、在财务、在工厂，都不是一个意思。" [seg 761–764]
- "大模型能够理解你的字段，但不代表它能理解你企业里的口径。所以我们要先把口径、指标统一下来 ... 企业里的口径其实是在变化的，所以要把决策过程也留下来：为什么变？变成了什么？什么意思？要可追溯。" [seg 805–812]
- "当企业语义不统一的时候，模型越强，给你的回答可能就越离谱，而且它会非常自信地给你一个非常漂亮的错误答案，甚至让你发现不了。" [seg 813–817]
- "第一个是词，也就是语义：一个词是什么意思？这块只能自己来梳理，别人帮不了。" [seg 846–855]
- "这里第二层也是最难的一层，因为目前市面上还没有什么非常好的产品" [seg 737–744]

d1b08 DataHub〔PR〕

- "People double-check a weird number before it goes into a deck. Agents don't." [seg 1687–1697]
- "Every major platform is actually building its own version of the context platform: AWS Context, Snowflake Cortex and Horizon, Databricks Unity and Genie, Microsoft Fabric IQ, Google's Knowledge Catalog ... Nobody else should own what "high-risk" means at your company. You should store it in a vendor-neutral format" [seg 1732–1743]

d1b10 Datus AI〔PR〕

- "one flight has 120 passengers. But if you join another table, like delayed flights, it may double or triple the number ... So we need a deterministic engine underneath the knowledge graph" [seg 1282–1298]
- "every vendor has its own semantic layer ... Snowflake, Salesforce, and dbt created this project under the name Open Semantic Interchange ... contributed it to the Apache Software Foundation as Apache Ossie." [seg 1326–1338]

判断：keep。HICAP 是非 PR 的落地方，给出问题本身；DataHub、Datus 只作市场事实：数据平台各建一套上下文层，中立厂商推开放格式（Apache Ossie）和确定性 SQL 运行时。HICAP 说"市面上还没有非常好的产品"，和卖方说法形成对照。

### B5. 整页网页撑爆上下文：只返回相关片段，先搜索再开浏览器 —— drop

- d1m14 Exa〔PR〕："For a fast agent, you should be retrieving the minimum amount of tokens possible for the next decision." [seg 1338–1345]；"the guiding principle here is search first. You're able to read the highlights of the page, and then identify what the task still needs." [seg 1332–1337]
- d2m20 Jina：处理后网页 token 远少于原始 HTML [seg 3721–3735]；"也许把网页转成 Markdown 并不是最后一步" [seg 3747–3751]

判断：drop。"少给 token"是常识，Exa 是 PR。Jina 的 token 数据只作为 B2 成本账的前提保留。

### B6. 小模型搜索会死循环、反复调用 —— drop

d1m05 You.com〔未列入 PR 名单，但主体是案例推销〕："death loop ... this is when a model will search over and over and over again without finding the right information" [seg 988–995]

判断：drop。属于模型后训练话题，已在 s3（RL 数据）覆盖。

### B7. 搜索 API 卖给 agent 和模型公司，附带授权结构化数据 —— drop

d1m05："We also have licensed structured data sources of information not found on the web, from things like the World Bank and S&P and Polymarket" [seg 913–922]；展商 Patsnap（专利、科研数据经 API/MCP 给 agent）、Brave（Search API）。

判断：drop。只是"谁在卖"，没有挑战层面的信息；s3 已写 You.com。

---

## C. 运行底座

### C1. 沙箱要有状态、短命、高并发；K8s 为长驻无状态服务设计 —— keep（市场事实，补上分歧）

d1m12 Daytona〔PR〕

- "It's ideal for running long-running, stateless web services. But with agents, the requirements are completely opposite. Agents need, number one, statefulness ... And most of the tasks agents do are short-lived" [seg 876–885]
- "if you want to achieve statefulness on Kubernetes, you have to mount some kind of external storage. And this is the trap, because once you do that, all of your file system operations go over the network, and your IOPS fall" [seg 929–939]
- 做法：本地快照、按使用频率分发快照、只传增量 [seg 901–921]

d1m19 Google〔PR〕

- "如果你是一个大规模实验室，在百万量级，或者是比它更小的实验，大部分情况下，我们目前的方案，叫 agent sandbox，基于 Kubernetes，已经能够满足你的需求。" [seg 2180–2184]
- 难点：单个任务多次 rollout 带来的起停量、镜像体积大、控制面崩溃、网络 identity 数量膨胀 [seg 2107–2124, 2160–2166]
- 做法：预热池、镜像就近缓存、控制面优化 [seg 2150–2159]

判断：keep。现有文本只写了 Daytona 的立场。两家都是 PR，结论相反：Daytona 说别在 K8s 上自建，Google 的开源方案就建在 K8s 上。共识在问题清单上：冷启动、镜像分发、状态保留。revised 只写分歧和共识，不采信任一方的性能数字。

### C2. 沙箱大部分时间在等模型，资源空闲 —— keep

- d1m19 Google〔PR〕："80% 的时间它都是空的，只有 15% 的时间在真正工作。80% 的时间是在等模型产生" [seg 2132–2137]；下一代 agent substrate 用快照快速起停压掉空闲 [seg 2173–2179]
- d1m03 Langfuse（非 PR）："this loop runs in our backend workers, not in a sandbox. The sandbox is just one tool available to it. That's what we would usually recommend folks do, because you save a lot of compute cost for the sandbox if you only use it when you actually need it" [seg 524–532]
- d1m09 StepFun〔PR〕："上面的云端harness更接近于脑 ... 下面是执行操作的手 ... 适合在隔离环境当中运行的操作，可以交给远端的sandbox。" [seg 474–479]
- d2m08 MiniMax（非 PR）："通过写一些调用工具的脚本，放在沙箱里面执行，可以更好地提高我们的 token 效率" [seg 1632–1648]

判断：keep。现有文本已有，核实准确。Langfuse 是非 PR 的直接建议，StepFun 的"脑与手"是同一结构。revised 以 Langfuse 为主。

### C3. 沙箱回收后文件丢失；自建备份恢复成本高 —— keep

d1m17 TiDB〔PR〕

- "sandbox 又挂载 EBS；一般任务结束后，我们就会回收 sandbox，同时清理策略也会把对应的 EBS 清理掉。这种情况下，虽然 meta 记住了很多东西，但是我们的文件都丢了。" [seg 1887–1890]
- "平台最终要维护一整套非常复杂的、可靠的项目备份和恢复流程" [seg 1891–1893]
- "能够把工作区独立于当前的 sandbox 持久存储：session A 写完之后，就可以把 sandbox 释放掉，session B 可以 mount 同样的文件系统" [seg 1894–1895]

展商 Tonbo："yield your agentic workload on your laptop and resume it anywhere"（开源嵌入式数据库）。

判断：keep，市场事实。现有文本把"文件丢失"和"冷启动慢"并成一行、归给 TiDB 和 Google，混了两个问题；revised 拆开：冷启动归 C1，文件归这里。

### C4. agent 交付的每个应用都要一个数据库，数量级远超传统 —— keep（新增，现有文本缺）

d1m17 TiDB〔PR〕

- "平台就面临一个更大的问题：agent 不断交付新应用，后面要持续保存不同应用的数据库。" [seg 1899–1902]
- "创建超时了，数据库到底有没有建成？重试会不会再重建一份？回收的时候有没有丢掉资源？ ... 所以代码生成越快，平台越需要一套能够跟上交付速度的数据库服务方式。" [seg 1903–1903]
- "没有人一开始就计划建设这么多的 AI infra，其实是用户的诉求把数据库推到了这里。" [seg 1944–1945]

判断：keep，市场事实。这是建站类 agent 平台的具体负担，现有文本漏了。

### C5. 改了 agent 无法判断是否更好：checkpoint + fork —— keep（压缩）

d1m17 TiDB〔PR〕

- "如果我们每次都从头重新跑，输入、工具返回、文件可能就发生了变化，结果就会有差异，这个变化到底来自策略还是来自现场的变化，就很难解释了。" [seg 1930–1930]
- "把已经保存的 meta 快照和 events，与文件系统保存文件的 checkpoint 绑定 ... 从文件系统里面 fork 出一个当时一模一样的文件内容" [seg 1931–1934]

判断：keep 但压缩为存储行的一部分。问题本身有价值（对比实验要固定现场），方案来自 PR 演讲。评测闭环本身属于 s5 和 s2 的范围。

### C6. RL 训练里基础设施故障被记成任务失败 —— drop（s5 已覆盖）

d1m19："这些情况有可能被 reward 评估为这个任务没有完成，比如内存溢出或者超时等等。这样你整体的训练数据其实就被污染了" [seg 2125–2131]

判断：drop，s5 已用。

### C7. 记忆与团队知识层 —— drop

d2m19 Nowledge（非 PR）："我们发现把 team harness 做相应的 compile ... 最好的方式是让 team context 以 harness adapter 的方式被 leverage" [seg 3630–3653]

判断：drop。属于记忆和上下文工程，和"企业知识"有交集但讲的是团队上下文如何接 harness，不是 infra 挑战；证据也是讲者自述实验，细节未展开。

---

## D. 规律候选

### D1. 现有基础设施默认"请求无状态、调用方是人"，agent 两条都不满足 —— keep（作为主结论）

依据：
- 无状态假设被打破：Optiver "the nature of an LLM request is stateful" [d1m16 seg 1695–1708]；Daytona "ideal for running long-running, stateless web services. But with agents, the requirements are completely opposite" [d1m12 seg 876–885]；TiDB 沙箱回收后文件丢失 [d1m17 seg 1887–1890]；Harvey 本地 agent 的上下文和轨迹不留存 [d1b02 seg 226–232]
- 调用方是人的假设被打破：Microsoft agent 冒用人的身份 [d1m02 seg 213–228]；Visa 网站把 agent 当 bot 拦、风控把机器交易当盗刷 [d1b04 seg 635–655]；Jina 匿名 agent 访问冲击免费模式和广告模式 [d2m20 seg 3752–3766]；HICAP 与 DataHub：人会凭经验核对口径和异常数字，agent 不会 [d2m04 seg 813–817; d1b08 seg 1687–1697]

判断：keep。现有文本的结尾规律（"有状态、生命周期短、并发量大、会越权"）方向对，但把四个并列特征混在一起，"并发量大"是程度问题，不是性质差异。改为两条假设，能覆盖三层。

### D2. 授权收窄到单次任务：身份层、调用层、支付层各自独立做了同一件事 —— keep（作为结尾规律）

- Microsoft：agent 有独立身份，权限低于其主人（`Files.Read.All` vs `Files.ReadWrite.All`）[d1m02 seg 272–284]
- 1Password：用户 grant 只到 read，越过的调用被拒或升级给人 [d2m16 seg 3078–3086]；判断标准是"调用是否符合任务" [seg 3103–3110]
- Visa：scoped token，当晚失效、有上限，消费须匹配用户意图和授权 [d1b04 seg 660–671]

判断：keep。三家分属操作系统/办公套件、密码管理、卡组织，互不引用，结构一致：凭证不再等于人，而是按这次任务的范围和时限签发。

### D3. 老牌厂商把原有控制点延伸到 agent —— drop

现有文本："做这层的公司有新创业公司（Daytona），也有转型的老牌厂商（TiDB 数据库、Visa 支付、1Password 密码管理）"。

判断：drop。属于名单罗列，读者从表格公司列就能看到；TiDB 的"被客户推着走"[seg 1944–1945] 已在 C4 用。

---

## 对照现有文本逐行结论

| 现有行 | 结论 | 说明 |
|---|---|---|
| 沙箱有状态短命并发，K8s 不适合（Daytona） | keep，补充 | 加上 Google 基于 K8s 的相反立场（C1） |
| 文件丢失 + 冷启动慢（TiDB、Google） | 拆分 | 冷启动并入 C1，文件持久化归 C3 |
| 沙箱空闲（Google、Langfuse） | keep | C2，以非 PR 的 Langfuse 为主 |
| checkpoint 分叉对比（TiDB） | 压缩 | 并入存储行（C5） |
| 协议翻译丢 thinking、破缓存（Optiver） | keep，扩展 | 加上 HTTP 200 不等于成功、首 token 前才能切换、功能取交集（A1、A2） |
| 越权，身份层限权 + 小模型审调用（Microsoft、1Password） | keep，拆开 | 身份限上限、调用审批管单次（A8、A9），并入结尾规律 |
| 数百个 agent 影响面（Dify、Microsoft） | drop | Dify 为 PR、观点常识；Microsoft 错配（A10） |
| 整页网页撑爆上下文（Exa、Jina） | drop | 常识 + PR（B5） |
| 公私模型统一网关（Raytone、Optiver） | 改归属 | Optiver 是多家公有供应商互备，公私混用的是 Techcombank（A4、A7） |
| agent 付钱被风控拦（Visa、Stripe、Adyen、Clink） | keep，扩展 | 加入网站拦截、Amazon 屏蔽 Muse、Jina 的付费争议（B1–B3） |
| 新增 | — | 企业口径（B4）、agent 读网页与广告模式（B2）、海量隔离数据库（C4）、缓存约束（A3） |
