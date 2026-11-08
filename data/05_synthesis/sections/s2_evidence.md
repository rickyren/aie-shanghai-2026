# s2 证据表：企业里大规模用 coding agent

检索范围：53 场 transcript 全部 grep（PR / pull request / code review / review / merge / CI / coding agent / Claude Code / Codex / monorepo / 注意力 / attention / 测试 / 员工 / team / semantic layer / 语义层 / 本体 / ontology），按 all_talks.json 摘要初筛后通读：d1m13、d1b02、d1b07、d1m10、d1b09、d1b05、d2m05、d1m03 全文；d2m19、d1m18、d1m02、d1m04、d2m04、d2m08、d1b08、d1b10、d1b03、offagenda_AJ_WaytoAGI 相关段落。

注：d1m10 的 transcript 有多段被合并标为 `[seg 505–505]`，照原样引用。

---

## A. 共享上下文与任务（协作）

### A1. Manus：mono repo + 任务公开化 —— keep
- d1m13 [seg 1012–1020]：「组织内的上下文其实是分散在不同的个人代码仓库，还有内部系统中的。当我们要让AI干活的时候，还是得有人先去收集这些上下文。」
- d1m13 [seg 1021–1027]：「一个是Manus mono repo，它里面包含了公司所有的代码仓库、知识库、内部工具……第二件事是任务公开化，就是公司里的每一个人都可以看到其他人的agent的任务是什么，你也可以直接加进去进行协作。」
- d1m13 [seg 1102–1111]：「你可以直接把任务链接发给那个能做决策的人，他就像看自己的Manus任务一样，看完上下文，可以选择直接追问，也可以选择当场就把决策做了，然后agent就会自己继续跑……mono解决了AI看不全上下文的问题，而任务公开化其实是解决人看不全上下文的问题。」
- 判断：keep。「mono 给 AI 补上下文，任务公开给人补上下文」这条区分有价值，是 section 的核心之一。

### A2. Manus：插件化架构减少跨仓库改动 —— keep（并入 A1）
- d1m13 [seg 1080–1086]：「我们把Manus完全变成了插件化的系统，由一个精简的内核加周围的外围功能模块组成……这样AI在开发的时候，可以更少地做跨仓库的工作。」
- 判断：merge 进 A1。为了让 agent 好干活去改系统架构，是现有文本没有的具体做法。

### A3. Manus：产品、设计同学自己提 PR —— merge（进 B5）
- d1m13 [seg 1062–1066]：「产品同学和设计师同学也开始积极地参与研发的工作……合了160多个PR。」
- 判断：merge 进 B5（审查分级）。单独看是常见的「非工程师也能写代码」，和审查机制放在一起才有信息量。

### A4. Harvey Specter：多人在 Slack 里和同一个云端 agent 协作，过程留痕变评测集 —— keep
- d1b02 [seg 208–213]：「同事拿到的是一个最后的缩影，并不知道 Agent 背后的故事。我希望的是，大家能把 Agent 所有的这些 context 一起放在我们的讨论中。于是多个人可以跟一个 Agent 协作」
- d1b02 [seg 214–215]：「这个产品现在公司大概 500 多人都在非常活跃地使用，产生了大概上万个 PR。我们根据这上万个 PR 得到的结果，成为了我们现在可以用的评测集。」
- d1b02 [seg 226–232]：「大家在本地跑的这些 Agent，最后 Agent 的 context、thinking traces 都不见了。但一旦我们有了这么一个大家都可以协作的 Agent，这就成了我们可以在线上收集的数据，并且是内部数据」
- 判断：keep。它把「协作」和「评测」两条线接起来：agent 放到云端共享，副产品就是自家评测数据。

### A5. Nowledge：团队上下文编译进 harness，比训进模型参数有效 —— drop
- d2m19 [seg 3630–3653]：「能不能把 team context 这些团队的智慧，一定程度上内化到你的参数模型中。我们试了九个不同的场景……只有三个情况是有收益的……把 team harness 做相应的 compile……效果反而更好」
- 判断：drop。讲者自己说「时间关系我就不展开」，实验设置和指标都没讲，没法核对；而且讲的是团队记忆产品方向，和 coding agent 协作实践关系弱。

### A6. Microsoft：同事的 agent 之间会临时互相调用，测试负担上升 —— drop
- d1m02 [seg 353–366]：「soon, it'll be my colleague's agent talking to my agent, and these agents may bring in still other agents.」
- d1m02 [seg 367–375]：「And what that means is that the burden of testing rises.」
- 判断：drop。这是预测，现场 demo 因断网没演示成；说的是一般企业 agent，不是 coding agent 内部实践。agent 身份和权限部分已在 s4。

### A7. WaytoAGI：做过两次的事写成 SOP / skill —— drop
- offagenda_AJ_WaytoAGI [seg 961–967]：「你可以把重复多次的事情的这些一两句话的prompt直接放到你的AGENTS.md里边」
- 判断：drop。substance_filter 标为干货少；内容是常识。

---

## B. 验证：让机器检查机器写的代码（PR 看不过来 + 测试爆炸）

### B1. Harvey：review 成了瓶颈，开始用 agent 审 PR —— merge（进 C 组，作为 Harvey 做评测的动因）
- d1b02 [seg 242–247]：「因为现在每个人都有更多的 output，所以 review，也就是审核 PR，也变成了瓶颈，大家渐渐会用 Agent 去审核 PR。那用什么样的模型、harness 或者 prompt 去审核 PR？也是我们最近在研究的问题。」
- 判断：merge 进 C1。

### B2. Data4Life：harness 当第一道 reviewer（spec / 旧系统 oracle / CI gates / 截图验证）—— keep
- d1b09 [seg 998–1002]：「nearly 300 PRs……it was too much code to really manually review every line.」
- d1b09 [seg 1010–1019]：「the specs to define what needs to be changed. Then the oracle, which is the legacy application Atlas 2 that you can compare our application to. The gates — that's the CI gates, the tests and other checks. And then visual verification via screenshots.」
- d1b09 [seg 1041–1052]：「We took these, uploaded them into the front end, imported them, exported them, loaded them, modified them, and ensured that they're still correct — and by that ensured that Atlas 2 and Atlas 3 come to the same result.」
- 判断：keep。

### B3. Data4Life：AI 写的测试会作弊，用变异测试检验测试本身 —— keep（最有信息量的一条）
- d1b09 [seg 1061–1068]：「we noticed that the agents are sometimes cheating in a way and creating tests which are always true. On the other side, we did mutation testing.」
- d1b09 [seg 1069–1079]：「for one component we had a test coverage of nearly 90%, so it looked great. But when we did the mutation testing, we noticed that less than 15% of the modifications were caught by the tests.」
- 判断：keep。指标层面的结论：coverage 高不代表测试有效，Data4Life 改看 mutation score。

### B4. Data4Life：harness 抓不到的缺口与适用范围 —— keep
- d1b09 [seg 1120–1135]：「What our harness is still missing……is environment assumptions……you need to make sure they fail reliably. We had situations where something was timing out, and that's not automatically noticed by the harness.」
- d1b09 [seg 1136–1140]：「The last part is probably the most important: domain judgment……it's quite hard to reliably define it in a general way」
- d1b09 [seg 1167–1172]：「If you already have a reference implementation, all the input is structured, you have a lot of sample inputs, and already a very good testing framework……quite manageable.」
- d1b09 [seg 1173–1184]：「It gets more challenging if you really start with a completely new product……quite often it makes more sense to have the human more involved in making the decisions.」
- 判断：keep。现有文本缺这条限定：这套做法适合有参考实现的重写，全新产品不适用。

### B5. Manus：人工审查只留给高风险模块 —— keep（新增）
- d1m13 [seg 1073–1079]：「如果他们用的coding agent已经是旗舰模型，我们的code review系统也是旗舰模型，再加上mono里面有很多架构设计、研发的准则，他们提上的代码质量其实是完全OK的。而且我们还建立了领域负责人的审核机制，像是支付系统、付费模块，或者是核心的prompt，都必须由对应的负责人同意之后这个PR才可以合。」
- 判断：keep。现有文本没提。它给了「人审哪些」的一个具体切法：按模块风险分级。

### B6. Instagram：给 app 暴露语义、状态和语义化动作，agent 像工程师一样验证 —— keep
- d1b05 [seg 735–737]：「on top of the UI we provide the accessibility tree and component semantics, we expose the app state and the configuration of the output file — then the agent is able to answer those questions.」
- d1b05 [seg 739–741]：「we ended up doing is building a CLI……where we give it the clip ID and the destination index, and by calling this CLI the agent directly finishes the reorder action in one tool call.」
- d1b05 [seg 742–742]：「The verification agent is a combination of fixtures and the LLM……For those setups we do not need the LLM, because they are deterministic」
- d1b05 [seg 743–744]：「By inner loop we mean that when writing code, the verification agent verifies the output of the coding agent……By outer loop we mean that for every eligible change, we run verification in continuous integration」
- 判断：keep。要点：为了让 agent 能验证，得改被测产品本身（加语义和 CLI），这和 Manus 为 agent 改架构是同一类动作。

### B7. Instagram：验证 agent 自我改进，人审 diff —— keep（并入 B6）
- d1b05 [seg 748–749]：「We have another agent scanning all those failures every day and proposing diffs to improve the agent. Humans review those diffs……we were able to improve the conclusive verification 〔?〕 rate」
- 判断：merge 进 B6。Instagram 跟踪的指标是 conclusive verification rate，以及每次验证的 tool calls 和 token（[seg 738–738]：「reduced tool calls on average……and reduced tokens」）。

### B8. Daily：人写成功标准，LLM 写测试和模拟用户，人检查 judge —— keep
- d2m05 [seg 900–906]：「We're flooded with so many pull requests……So even if we could all read English and Chinese perfectly, there's just too much information to check.」
- d2m05 [seg 907–912]：「We have to stop checking the work itself and start checking the checkers.」
- d2m05 [seg 973–980]：「I don't necessarily need to know the test, but I can double-check the success criteria.」
- d2m05 [seg 1004–1008]：「machines are doing the work, judges are checking the work, and then humans check the judges.」
- 判断：keep，但降为一句。案例是个人 demo（奶茶语音 agent），企业实践成分弱；可取的是「人只检查成功标准和 judge」这一分工。

### B9. OpenClaw：agent 自己加测试导致 CI 成本和等待失控 —— keep
- d1m10 [seg 524–534]：「my concern wasn't the cost of the compute; it was that more and more tests were being added by agents as they were coding……if we delete the tests, then we have no way of verifying the agents have actually done any work……I'm waiting 30 minutes on every single PR. This starts to slow down the whole entire factory」
- d1m10 [seg 543–551]：「the volume of commits actually eclipsed and started to become a real bottleneck for us.」
- 判断：keep。

### B10. OpenClaw：主干不再逐次跑 CI，改为定时批量 + 发版前全量 —— keep（修正现有文本）
- d1m10 [seg 552–557]：「we turned off CI checks on main entirely. What happens now is you have a limited check that happens on a PR, the agent goes through the review process……once that PR is merged, main doesn't do a CI check. That happens every, say, 30 minutes to an hour, and we have some more extensive testing that happens as part of our release process.」
- 判断：keep。现有文本只写「关掉主干上的逐次 CI」，漏了「定时批量跑 + 发版前全量」，读者会误以为主干不测了。

### B11. OpenClaw：用分类器预测回归风险、只跑相关测试（adaptive testing）—— keep，但要标注尚未全面启用
- d1m10 [seg 565–575]：「This was merged into our main codebase in the last few days and hasn't been fully activated yet」
- d1m10 [seg 576–585]：「building a model of proof, using classifiers and tree-based classifiers, to see — based on the code that was changed and what was executed — whether we can get a good understanding of what has a likelihood of regression, and then just test that component……So what I'm hoping for is……reduction in our total CI cost」
- 判断：keep，必须改写。现有文本写成已落地，原文是刚合入、没全面启用，降本是讲者的预期。

### B12. OpenClaw：review agent ClawSweeper 跑在每个 PR 和 issue 上 —— merge（进 B 组表格的 OpenClaw 行）
- d1m10 [seg 505–505]：「ClawSweeper, which is essentially our review agent that runs across every PR and issue……even then things would regress, things would break after release」
- 判断：merge。说明 review agent 本身不够，这也是 OpenClaw 转向「proof」的原因。

### B13. 展商 Sonar：AI 生成代码的质量与安全检查 —— drop
- exhibitors.csv：Sonar，「AI 生成代码的质量与安全检查」，展位 demo「Using SonarQube to Support AI Agent-Driven Software Development」。
- 判断：drop。只是展商自述卖点，没有现场讲者说明它解决了上面哪一个具体问题；「代码验证有商业产品」对有经验的读者价值低。

---

## C. 选型与评测：用自家已合并 PR 回放

### C1. Harvey：回放内部 PR + LLM judge，一次只改一个变量 —— keep
- d1b02 [seg 223–225]：「因为 harness 和模型都是可以替换的，所以一个 task 从最开始到最结束，这个固定的流程都是可以重放的。这个固定流程就变成了我们的一个 evaluation case」
- d1b02 [seg 264–273]：「通过 replay 的方式，再通过一个 LLM judge 去评分，最后就可以判断出我们到底是改模型、改 harness，还是改其他东西……最后我们发现，模型和 harness 都不是真正要改的东西……每次只改一个变量」
- 判断：keep。

### C2. Harvey：差距常在自家代码和流程，PR description 例子 —— keep
- d1b02 [seg 282–285]：「即使我换了模型、换了 harness、换了真正的 prompt，也没有什么变化。很多问题其实发生在我丢给它的数据上……当你这个 PR 的描述太长的时候，你最后给它的东西并不是真正能用上的东西，于是它漏了很多东西。」
- 判断：keep。

### C3. Harvey：评测集的难点在挑干净的 case —— keep（新增，现有文本漏了）
- d1b02 [seg 289–295]：「我们发现收集了那么多数据，真正能用的并不多……如果你要把它重放一遍，有可能这个 code review 本身有另外的人或者 Agent 在上面留了更多的 code review，那你重放的过程中，这个 Agent 可能会受到后来那些 signal 的影响……所以我发现花更多时间的是研究这个评测集该怎么选出来。」
- 判断：keep。做过回放评测的人才会知道的坑：后来的 review 和改动会泄漏答案。

### C4. Harvey：code review 上便宜的开放权重模型接近顶级闭源 —— keep（措辞收窄）
- d1b02 [seg 296–301]：「当我们保证 prompt 是 optimal 的，并且 harness 是比较通用的情况下，DeepSeek V4.1 的 Flash 已经能够接近 Opus 的效果……Opus Max 会花非常多的钱，但它真正能 catch 住的东西有多重要呢？进行了一些人类审查之后，发现其实可能并不重要。」
- 判断：keep，限定在 code review 任务，并带上前提（prompt 已调优）。现有文本泛化成「接近顶级闭源模型」，范围说大了。

### C5. Harvey：fix CI 上开放模型也能过，但重试多、占沙箱时间 —— keep
- d1b02 [seg 302–307]：「fix CI 的结果是非常好确定的：CI 到底是过了还是没过……区别在于 Opus，它有时候一遍就过，但其他模型可能需要不断反复地尝试，所以会花很多很多时间，甚至有可能浪费你的沙盒运行时间」
- d1b02 [seg 308–314]：「这些 open weight 模型大部分时间都在思考更多，需要更多的 thinking trace」
- 判断：keep。说明选型要看的指标：结果可判定的任务（CI 过没过）比的是耗时和重试，不是通过率。

### C6. Agoda：回放已合并 MR，对照 golden tests 做 A/B —— keep
- d1b07 [seg 891–896]：「let's take our merged MRs, replay them, and learn something from them……we evaluate our results against the golden tests that we already have in the merged MR.」
- d1b07 [seg 897–899]：「On the A side we remove all the context, and on the B side we keep it as it is. The result was surprising: the solution rate was the same, but the cost was 8% higher with our context.」
- 判断：keep。「精心维护的 context 不提高解题率、只增加成本」现有文本没写，是有反直觉价值的一条。

### C7. Agoda：同一工具在另一个仓库结论相反 —— keep
- d1b07 [seg 902–906]：「We ran the test against another repository, and this time we got completely opposite results: 30% higher cost.」
- d1b07 [seg 907]：「we should focus on our own benchmark and our own repositories.」
- 判断：keep。

### C8. Agoda：从 reviewer 打回意见里找 context 冲突，产出 context 补丁 —— keep（新增）
- d1b07 [seg 908–911]：「we focus on three evals: accepted human reviews, our tests, and also behavior checks generated by an LLM judge……The output we expect from the skill is a context MR, a patch that will improve our context over time.」
- d1b07 [seg 915–918]：「In the AGENT.md file we had the instruction: if you want to put in a new contract, please put it in the command folder……the reviewer……pushed back with the comment, "Oh, this should be in the core folder, please redo it." This exact case happened three times」
- 判断：keep。回放的产出物是对 context 文件的修补，和 Harvey「问题在自家流程」是同一个结论的两种证据。

### C9. Agoda：推荐复用 Harbor 评测框架 —— drop
- d1b07 [seg 919–924]：「reuse an open source evaluation framework……Harbor」
- 判断：drop。工具推荐，价值低。

### C10. OpenClaw：自建 ShellBench，少用合成数据 —— drop
- d1m10 [seg 598–601]：「One thing we're seeing a lot of companies doing now is developing their own internal benchmarks. Try to stay away from synthetics」
- 判断：drop。ShellBench 是个人 agent 产品 benchmark，不是内部 coding 实践；「自建内部 benchmark」已由 Harvey、Agoda 覆盖。

### C11. Techcombank：组织级 token 成本指标 —— drop
- d1m18 [seg 1967–1972]：「the effective blended cost per million tokens. It is basically the cost of input and output of the whole organization, after the caching rate.」
- d1m18 [seg 1973–1976]：「we tend to want to use the best model out there, such as Opus.」
- d1m18 [seg 2019–2025]：「most of us run Claude Code with $200 plans and it's just not enough, and we run into overage.」
- 判断：drop。讲的是推理采购方式（订阅 / 按 token / 自建 GPU），和 coding agent 的协作、评测实践不在一条线上；放进来会稀释主结论。

---

## D. 人的注意力与判断

### D1. Manus：自动接单 bot 提 PR 的速度远超合并速度，没人定优先级就是浪费 token —— keep
- d1m13 [seg 1117–1125]：「它提PR的速度远远大于我们合PR的速度，几天下来有几十个PR没人管、没人合，而且你并不知道这些PR的优先级是什么……如果没有人去定优先级，AI的自动化研发很可能只是在浪费token而已。」
- 判断：keep。

### D2. Manus：注意力不可再生，常规决策沉淀成 skill / memory —— keep
- d1m13 [seg 1138–1147]：「token是一个可再生资源，而人的注意力变成了一个不可再生资源……不要平均地分配你的注意力……那些很常规的决策，其实应该想办法把它们沉淀成skill，沉淀成agent的memory」
- 判断：keep。

### D3. Manus：「自动驾驶」很贵，复杂需求要人做方案、拆任务、分阶段验证 —— keep
- d1m13 [seg 1148–1162]：「我们有一位同事一个月花了10万美金的token……对于复杂的事情，你还是要做好方案设计，做好任务的拆分，做好阶段性的验证。」
- 判断：keep。不引用金额。

### D4. Manus：需要复合型人才 —— drop
- d1m13 [seg 1129–1137]：「一个有产品sense的研发同学，他写出来的功能会更好用；一个懂一点代码的产品同学，他提交的PR可能是一遍就过的。」
- 判断：drop。常识，低价值。

### D5. OpenClaw：前台工作先定义 proof，后台工作自动验证合并；跟踪 agent cycle time —— keep
- d1m10 [seg 505–505]：「we also have this concept of foreground work. These might be features or things you're working on that require a lot of human attention. Even in these cases, more and more I'm getting to a point of asking: how can I define the proof or the outcome before the actual work happens?」
- d1m10 [seg 505–505]：「In terms of background work — particular fixes and issues that can be validated — it's going to automatically test, validate, and merge.」
- d1m10 [seg 535–542]：「Agent cycle time looks at the time from when the PR was opened to when the PR was merged, and we track this over time.」
- 判断：keep。「人把注意力花在事前定义 proof」与 Manus 的「定优先级」互补。

### D6. Langfuse：人保留质量定义、可信反馈信号、发布决策 —— merge（进 D 组）
- d1m03 [seg 557–561]：「it uses the one resource you probably can't scale in your organization: the engineers working on your agents.」
- d1m03 [seg 608–616]：「what remains for humans to do? In our view, that's mostly quality. You need to own the outcome. What does good look like for your application? What are the feedback signals you use……And then the decision to actually release fixes」
- 判断：merge。讲的是 agent 产品的改进循环，不是内部 coding 实践；作为「人保留什么」的旁证并入 D。

### D7. Nowledge：夜间和周末 agent 工作的验证环节无法完全脱离人，按批次 steer 和 verify —— merge（进 D 组）
- d2m19 [seg 3604–3618]：「这种 semi-loop 的核心就在于它的 verification 环节是不能完全 decouple human 的……你大概还是要以 batch 的方式去 steer、去 verify」
- 判断：merge，作为旁证一句带过。

### D8. Instagram：人退出执行环节，负责验证、解堵和规划 —— drop
- d1b05 [seg 749–758]：「The human is now responsible for doing the verification, unblocking the agent, and doing the planning」
- 判断：drop。和 D1–D5 重复，且表述泛。

### D9. Ryo Lu：工具应像工作台，让人看得见计划、随时介入 —— drop
- d1m04 [seg 748–755]：「我可以看见它打算改什么……也可以在它开始动作之前介入这个计划」
- 判断：drop。个人工具设计观点，不是企业内部实践。

---

## E. 企业语义层与本体

### E1. HICAP：语义只能自己梳理 —— drop（不在本节）
- d2m04 [seg 846–855]：「第一个是词，也就是语义：一个词是什么意思？这块只能自己来梳理，别人帮不了。」
- 判断：drop。讲的是制造业智能体落地，与 coding agent 无关；原文不支持把它并进本节。

### E2. DataHub：业务定义别锁在平台方的上下文层 —— drop
- d1b08 [seg 1732–1743]：「we really urge all enterprises to own your own business logic. Nobody else should own what "high-risk" means at your company.」
- 判断：drop。substance_filter 标为产品发布；主题是数据 agent，不是 coding agent。

### E3. Datus：语义层之上加可执行本体 —— drop
- d1b10 [seg 1207–1212]：「moving from semantic layers to executable ontologies with Apache Ossie」
- 判断：drop。substance_filter 标为产品宣传；主题是数据 agent。

---

## 对照现有文本

| 现有条目 | 处理 |
|---|---|
| 协作（Manus、Harvey） | keep，补上「mono 补 AI 的上下文、任务公开补人的上下文」和插件化架构 |
| PR 看不过来（Data4Life、Instagram、Daily） | keep，补上 AI 写的测试会作弊、coverage 与 mutation score 的落差、适用范围限定；补 Manus 按模块风险分级人审 |
| 测试爆炸（OpenClaw） | merge 进验证一点；修正：主干改为定时批量跑、发版前全量；adaptive testing 刚合入、未全面启用 |
| 展商 Sonar | drop |
| 选型（Harvey、Agoda） | keep，收窄 Harvey 结论到 code review；补评测集选 case 的泄漏问题、Agoda context A/B 结果和 context 补丁 |
| 人的注意力（Manus） | keep，补 OpenClaw 前台/后台分工和 cycle time 指标、Manus 的「自动驾驶」教训 |
