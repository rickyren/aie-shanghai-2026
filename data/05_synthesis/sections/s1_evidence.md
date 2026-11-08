# s1 证据表：实时可交互的音视频

检索范围：用 all_talks.json 初筛后，在 53 篇 `data/03_clean/*.md` 中 grep 了 实时 / 全双工 / 打断 / 语音 / 视频生成 / 端到端 / 多模态 / real-time / duplex / interrupt / voice / speech / STT / TTS / latency / diffusion / frame 等词，并通读了 d1b06、d2m05、d2m06、d2m10 全文，以及 d1m11、d2m07、d2m01、d2m02 的相关段落。exhibitors.csv 里没有做实时音视频的展商。

判定：**keep** 写入正文；**merge → X** 并入某一点；**drop** 附理由。

---

## A. 实时对话：链路怎么拆（Cookiy, d1b06）

### A1. 全双工、可打断的级联管线已是通用件，不构成差异
- d1b06 [seg 775–777]：「我们用的技术栈其实跟 AI 客服的系统基本上是很类似的，大家都知道 VAD、STT、LLM、TTS 的整条管线。你在 Agora、LiveKit、Pipecat 上都大同小异，1.3 秒之内要完成下一轮的 time to first spoken word，对吧？然后你做得好一点，是全双工，做得差一点，就是能随时打断等等。这些在技术上我觉得没有太大的区别。」
- 判定：**merge → A2**，作为背景一句。追踪的指标：time to first spoken word（首句发声时间）。不写具体秒数。

### A2. 访谈场景比客服难在哪：同时看脸、看共享屏幕、接旁听者的小纸条
- d1b06 [seg 778–786]：「区别在哪呢？是我们的模型需要看见人……另外，我们很多时候需要受访者去共享他的屏幕，我们的 AI 还要一边看着他的脸，一边看着他分享的屏幕，然后去追问一些问题……所以这个对 context window、对实时的效果要求是很高的。」
- d1b06 [seg 787–793]：「他们要能持续地向这个 AI 塞个小纸条……所以这个 AI 不仅要实时地思考、实时地提问，它还要实时地听到背后的 researcher 或者业务方提过来的诉求。」
- 判定：**keep**（用作 P1 的场景前提）。现稿写的是「接旁听者的插话」，原文是旁听者给 AI「塞小纸条」，不是对受访者插话。已更正。

### A3. 大小模型配合（快模型说话、慢模型思考）失败
- d1b06 [seg 794–802]：「第一条弯路，就是所有人脑子里的第一想法：好，那我用大小模型配合不就行了吗？包括 GPT-Live，包括 Thinking Machines 的 interaction model，不都是大小模型配合吗？……因为那个大模型的思考——为什么它大，就是它太慢了。所以等大模型思考出来"我下一个问题应该问什么，是不是应该跳过，是不是应该结束"的时候，小模型早就在聊下一个话题了。而且很多时候大模型会被小模型带偏，不管怎么调，这东西我们就是调不好。」
- 判定：**keep**。现稿漏了这一点。它和端到端方案并列，是 Cookiy 试过并放弃的两条路之一，而且直接反驳了一种主流架构。

### A4. 端到端实时模型在这个场景不可用
- d1b06 [seg 803–806]：「端到端的模型特别牛逼……但是在这个场景下它不 work。为什么呢？它没有办法做屏幕共享，没有办法处理各种复杂的多模态的音频输入、文字输入，那个复杂的指令遵循它也做不到。实时模型的 thinking 能力确实比较差，所以就做不到。」
- 判定：**keep**。现稿只说「推理能力跟不上」，原文列了四条原因：不能做屏幕共享、不能处理复杂多模态输入、做不到复杂指令遵循、thinking 弱。

### A5. 最终方案：判断、动作、回复拆成三类子 agent 串联
- d1b06 [seg 807–813]：「把判断这件事情、下一步应该要做什么的 actions，以及具体怎么回的 response，这三个东西拆开来，拆成三大类的子 agent，每一大类的子 agent 都给一堆最好的模型、最快的模型。本质上这东西是串联的。但为什么串联的效果可能比前面的反而更好呢？因为它是串联，所以它不太容易串信息；其次是前面这两个你能够做得很快很快」
- 判定：**keep**。

### A6. 用冗余调用压延迟：同一请求并发多次、多家，取最快的
- d1b06 [seg 814–819]：「同一个模型，你用完全一样的输入去 call 它，它的 latency 是不一样的。我们因为成本不受限制，所以同一个模型我就 call 五次，看谁最快；我甚至可以 call 多家的同一个 API，每一家我都 call 五次，看谁最快……比如说模型突然抽风了，它输出的 JSON 格式不对了……你都可以暴力解决。」
- 判定：**merge → A5**。这个做法成立的前提是 A7。

### A7. 优化目标是 insight per minute，模型成本不是约束
- d1b06 [seg 765–771]：「最关键的不是用 AI 进一步降低 AI 访谈员的成本，而是利用 AI 来尽可能地达到一个高效的人类访谈员的水平。所以我们优化的最终指标叫做 insight per minute」
- d1b06 [seg 772–774]：「我们用模型的时候，很多时候是尽可能地用最好、最贵的模型……我们其实没有那么 care 模型的成本」
- 判定：**merge → A5**。说明为什么能用冗余调用换延迟。追踪的指标：insight per minute。

### A8. 离线大模型复盘整场访谈，回头改实时 harness
- d1b06 [seg 843–851]：「我们的对话虽然发生在实时，也就是说模型在此时此刻的 1.3 秒之内，就得想出来到底要问什么问题，还是要结束这个对话；但是整个访谈结束之后……我们能把整个访谈所有的音频和文字全都塞给一个更大的模型——你直接扔给 Claude Code，让它慢慢分析——它总是能分析出来：刚才那个问题提得好像不是很对……然后用离线的分析，再去改实时场景下的那个 harness」
- 判定：**keep**。现稿漏了。实时环节做不了的深度思考由离线环节补上，这一条直接支撑主判断。

### A9. 用历史坏案例（精确到某一轮对话）做 benchmark
- d1b06 [seg 830–838]：「把历史以来，要么是客户觉得不好、要么是我们自己觉得不好的所有场景，全部抓下来。场景细到什么程度？就是一个 30 分钟的访谈，其中在第 15 分 20 秒的时候，人类回了一句话，然后 AI 问了那个问题，然后客户觉得你问的这个问题好像不太对……然后把这些样例做成我们的 benchmark。诚然，每一次的优化就像打地鼠一样」
- 判定：**merge → A8**。离线环节的评测基准就是这批案例。

### A10. 半自动 RSI 容易掉进局部最优
- d1b06 [seg 839–842]：「后来我们演进到了所谓的半自动的 RSI……但这东西是一个很危险的方式，因为它很容易优化到一个局部最优，而那个局部最优可能是一种很奇怪的方式。」
- 判定：**merge → A8**，作为风险提示，一句话带过。

### A11. 中文长 prompt 指令互相冲突，砍短后又快又好
- d1b06 [seg 852–860]：「你写一个 8000 字的 prompt，很多时候中间有一些指令是相互冲突的……不仅 latency 变大了，而且很多时候会有很多 mal-behavior。所以我们最后把 prompt 本身砍到大概 1/3 的时候，速度变快，效果还变得更好。」
- 判定：**drop**。prompt 越短越好是常识，和实时场景关系不大。

### A12. 坚持不做后训练，只做 harness
- d1b06 [seg 861–872]：「我坚定地相信 harness 本身有好大好大的发挥空间……post-training 看上去很爽，但不是一个好的解法。」
- 判定：**drop**。这是 harness 和后训练之争，不属于本节；而且讲者自己也说有的场景不后训练不行。

### A13. AutoArk：全双工可打断链路是硬件厂商的大块工程成本，打包成 SDK 卖
- d1m11 [seg 713–718]：「所谓小算力设备，通常指的是智能眼镜、耳机以及小型的 AI 陪伴机器人……它主打的场景就是 AI 实时交互，所需要的就是 AI 的音视频对话」
- d1m11 [seg 731–740]：「整个全双工、AI 可打断的对话链路也是非常大的工程成本。在这一块……我们也提供了一套一站式的 AI 交互开发套件，我们把它叫做 EVA SDK……以及全双工的 AI 对话链路」
- 判定：**merge → A1**，只作市场事实（d1m11 在 substance_filter 里标为宣传）。它佐证全双工链路已经被做成现成部件出售。

### A14. AutoArk：简单意图走端侧全链路，开放问答才上云
- d1m11 [seg 813–820]：「如果用户是一个非常简单的意图，比如说查询我的心率，我们会由全端侧链路，从 ASR 到 TTS 播报……如果用户是一个开放式问答……它才会发起一次云端调用。」
- 判定：**drop**。属于宣传场次，降本数字无法核实；端云路由放在端侧 AI 主题下更合适。

### A15. World Labs：System 2 慢推理和 System 1 实时感知控制分层
- d2m01 [seg 248–253]：「higher-level, slower reasoning in System 2; real-time perception and control in System 1……Reasoning needs to incorporate what the System 1 loop currently believes……and it can then create or modify policies that work in real time.」
- 判定：**drop**。讲者明说这是示意架构（"one proposed organization rather than a required architecture"），语境是机器人和世界模型。它和 A3 正好相反，但不在同一场景，硬放在一起比较会误导。

---

## B. 实时视频生成：程序和生成模型怎么分工（Tripo, d2m10）

### B1. EdenLive：游戏引擎管规则、运动和比分，生成模型管画面
- d2m10 [seg 1829–1838]：「Look at the small window: that's what the game engine is rendering. And if you look at the main screen, EdenLive takes that simple scene and generates the richer visuals you are seeing in real time as you play. The game engine handles the rules, the movement, and the score. EdenLive handles how the world looks.」
- d2m10 [seg 1929–1939]：「The program decides whether the submarine has reached the treasure and where to pick it up. EdenLive receives that unfolding scene and renders it. So the game has a clear objective, and the visuals follow what actually happens in the program.」
- 判定：**keep**。

### B2. 分工原则：能描述的交给 agent 写代码，只能辨认的交给模型学
- d2m10 [seg 1885–1894]：「An agent can write a lot of what we can specify: put a door here, make it open, keep track of the score. A model can learn details that are much harder to specify: the face of a character, the shape of a creature……if you can describe it, an agent can write it; but if you can only recognize it, a model has to learn it.」
- 判定：**keep**，并进 P2。

### B3. 触发原因：coding agent 不用 Tripo 就能用代码搭出室内场景
- d2m10 [seg 1862–1884]：「these indoor scenes were built entirely in code by agents, in tens of seconds, and no AI-native 3D model like Tripo was used. One of the researchers said, "I haven't found an indoor scene that has to use Tripo."……A lot of a room can be specified」
- 判定：**merge → B2**，交代这个分工是被 coding agent 逼出来的。

### B4. 世界状态显式放在程序里，换镜头、换风格，状态不变
- d2m10 [seg 1909–1923]：「Keep the world state explicit: the program knows what happens……Then let a learned model render what you see. So you can change the camera or the visual style, and the state is still there」
- d2m10 [seg 1924–1928]：「You put out a fire, and it stays out. Leave a mark on the wall, and someone who arrives later sees it too. And two players can look at the same race from different cameras, because both views come from the same state.」
- 判定：**merge → B1**。

### B5. 接口是参考画面，每个游戏不用单独给模型做状态接口
- d2m10 [seg 1940–1949]：「EdenLive takes that view, a target first frame, and a text prompt, and generates the next frame. Important events can also arrive as short text descriptions……The useful part is the interface: reference footage. It can come from a game engine, an animation tool, or another program. Each game doesn't need its own custom state interface to the model.」
- 判定：**keep**。现稿漏了。这是让分工能通用的关键设计。

### B6. 开源范围和指标
- d2m10 [seg 1950–1954]：「With the 5-billion-parameter model, our demo setup reaches 720p at 24 frames per second. There's also an offline mode for rendering existing footage.」
- d2m10 [seg 1970–1976]：「EdenLive is open source under Apache 2.0 — the model weights and the streaming interface code」
- 判定：**merge → B1**。只写开源了权重和流式接口代码；指标只写 Tripo 报的是分辨率和帧率，不写数字。

### B7. 应用：游戏预览、动画换风格、真实素材重渲染
- d2m10 [seg 1955–1960]：「keep the layout and the motion, change the look. That opens up game previews, different treatments of animation, and re-rendering real footage. In the game examples, the program still owns the score; changing the style doesn't change who got hit.」
- 判定：**keep**。这是本节和内容行业最直接的连接点。

### B8. 未解决的问题：角色回到画面时细节漂移、灰盒控制不够、缺评测
- d2m10 [seg 1977–1982]：「a character can come back into view with details that have drifted, so we need better memory. Users need more control over what each grey box becomes.」
- d2m10 [seg 1983–1991]：「One of our agents actually passed a walkability check……which is definitely not correct. So we really need tests that capture what people actually mean by a world that works.」
- 判定：**keep**，并进 P2。角色一致性对内容生产是硬约束。

### B9. 用 EdenLive 把人手替换成机械臂，生成机器人示教数据
- d2m10 [seg 1961–1969]：「EdenLive replaces the hand with robotic arms, while keeping the motion and scene layout……We still need to test the physical accuracy and the usefulness for robot learning.」
- 判定：**drop**。属于具身智能方向，讲者自己说还没验证。

### B10. 线性资本：实时视频生成是他们在试的垂直方向
- d2m07 王淮 [seg 1244–1253]：「目前我们看到有一个垂直的应用，比如 real time 的 video generation，实时视频生成。因为这个跟大模型本身的战场有一点差异……那个东西主要还是基于 diffusion 的，它的目的是把速度提高到原来的 20 倍以上，可以把一些特殊的应用展现出来。所以我们也是被迫的，基于这些思考，绕开一些主模型的主战场，在某种意义上也是在 Y 轴上的一些尝试。」
- 判定：**merge → 内容行业段**，作为市场信号。现稿写「在投实时视频生成，认为它绕开了大模型的主战场」，原文是「被迫」绕开主战场的「尝试」，而且讲者说垂直方向「目前没有很好的答案」。已按原文改写。

### B11. HeyGen HyperFrames：agent 写 HTML 渲染成视频
- d2m02 [seg 372–380]：「we threw out our JSON completely and just let agents write HTML……with the framework you can render an MP4 video out of it.」
- 判定：**drop**。不是实时交互，归视频 agent 和上下文工程主题。

### B12. Kimi：video to game skill 把视频预告片转成可玩游戏
- d1m20 [seg 2221–2227]：「有了 video to game 这个 skill 之后，很快就可以把这样的预告片转化成一个真实可以 play 的游戏。」
- 判定：**drop**。属于宣传场次，也不是实时生成。

### B13. 视频、短剧是 AI 应用的重要方向
- d2m07 刘勇 [seg 1275–1283]：「第三个方向，当然就是视频了。前段时间不是看到那个图，有个上市公司说，中文 AI 世界 token 消耗 55% 是短剧」
- 判定：**drop**。讲的是视频整体，不是实时交互；数字是转述的二手信息。

---

## C. 实时听写和语音 agent 测试（KouShi d2m06，Daily d2m05）

### C1. STT 没有被解决，转写里经常出现没人说过的内容
- d2m06 [seg 1039–1045]：「Speech-to-text models have been around for years, and people think they're the solved part. But here's what we see.」
- d2m06 [seg 1051–1055]：「almost one in four of our practice sessions contained text that no one said. This is a big number, and it directly impacts the quality of our voice agent's replies.」
- 判定：**keep**（不写比例）。追踪的指标：含「没人说过的文字」的会话占比。

### C2. 公开基准和自家音频差距大，原因有两个：说话人和流式喂法
- d2m06 [seg 1071–1076]：「when we ran the same models on our own audio datasets, they showed error rates 4 to 20 times worse than what the benchmarks were telling us」
- d2m06 [seg 1077–1082]：「FLEURS uses audio from native speakers who read prepared sentences aloud, whereas our speakers are non-native speakers who think out loud while they're speaking. Second, FLEURS passes in the entire audio at once, whereas our audio flows through the pipeline I showed you, where the VAD chunks it into segments before feeding it into the STT models.」
- 判定：**keep**（不写倍数）。

### C3. 控制变量后的结论：问题出在 VAD 切出的短片段，不在说话人
- d2m06 [seg 1083–1089]：「We kept the same speakers and the same models, and this time fed the entire audio to the models……all these models showed a sharp increase in accuracy, and none of them produced any foreign script. So we concluded that nothing was wrong with our speakers.」
- d2m06 [seg 1090–1096]：「because the speaker was not very fluent and took a lot of pauses, the VAD chunked it into very short segments……You get transcriptions in different languages.」
- 判定：**keep**。现稿完全漏了这一点。流式处理本身就是错误来源。

### C4. 机制：decoder 的第一个 token 是语言，片段太短时语言一猜错就全错
- d2m06 [seg 1105–1112]：「the first token it transcribes is the language. So for a very short audio segment where the language guess is incorrect, all the tokens following it will be predicted in the wrongly guessed language……if you feed the decoder a bigger audio segment, it has access to more tokens and hence more context」
- 判定：**merge → C3**。

### C5. 解法：显式指定语言，把 VAD 的停顿阈值调长，不需要等整段
- d2m06 [seg 1119–1125]：「But we cannot wait for the entire audio recording before transcribing it, right? Because then our conversation is no longer live……When you tell the models the language they are supposed to transcribe in, you can regain 11% of that 20% gap. What is the remaining 9% gap? That gap is context.」
- d2m06 [seg 1126–1131]：「If you tune it so that it waits for a longer pause before cutting the audio segment, instead of cutting at the first short pause, you'll accumulate bigger audio segments and hence provide more context」
- d2m06 [seg 1135–1138]：「run your models on your own users' audio, tell them the language they are supposed to transcribe in, and let them hear more of the audio.」
- 判定：**keep**（不写百分比）。追踪的指标：按片段长度分档的转写准确率。

### C6. Daily：音频模式的模拟测试能发现文本模式发现不了的 STT 错误
- d2m05 [seg 981–985]：「Text mode is way faster because you don't have to generate any of the audio……And audio mode uncovers issues that text mode just won't surface.」
- d2m05 [seg 986–991]：「When I was running audio mode, I discovered there was a bug in the speech-to-text processor. Sometimes when I said "qu bing" (去冰), which means no ice, it heard it as "two 瓶"……And that's an issue that a pure text mode test just would never have caught.」
- 判定：**keep**。和 C3 是同一个结论：错误出在音频进入链路的方式上，只有用真实音频才测得出来。

### C7. Daily：人工语音测试太慢，用 LLM 扮用户并发跑模拟
- d2m05 [seg 934–939]：「voice testing is really slow when you do it manually, even slower than clicking through a web page……you have to do the whole conversation over and over and over again every time you make a small change.」
- d2m05 [seg 992–996]：「I can run 10, 20, 100 simulations all at the same time every time I make a small change」
- 判定：**merge → C6**，半句带过。「人只写成功标准，LLM 写测试」这部分 s2 已经用了，本节不重复。

### C8. Pipecat 是厂商中立的语音 agent 管线
- d2m05 [seg 913–926]：「a voice agent is a pipeline……Pipecat doesn't care. It's completely open source, completely vendor-agnostic, and completely free to use.」
- 判定：**drop**。管线结构是常识，后半句是产品介绍。

---

## D. 现稿逐条核对

| 现稿说法 | 核对结果 | 处理 |
|---|---|---|
| 全双工、可随时打断已是标准管线 [d1b06] | 原文支持（A1） | merge，降为 P1 的背景 |
| AutoArk 给眼镜和耳机提供端侧全双工对话套件 [d1m11] | 原文支持（A13），但属于宣传场次 | merge，只作市场事实 |
| Tripo 开源了实时生成渲染模型 EdenLive [d2m10] | 支持（B6） | merge 进 P2 |
| 线性资本在投实时视频生成，认为它绕开了大模型的主战场 [d2m07] | 部分失真：原文是「被迫」「尝试」，而且说垂直方向「目前没有很好的答案」（B10） | 改写，移到内容行业段 |
| Tripo 的 agent 和生成模型分工 [d2m10] | 支持（B1、B2） | keep，补上接口设计（B5）和未解决问题（B8） |
| 端到端模型推理能力跟不上，改用三段串联 [d1b06] | 支持但不完整：漏了大小模型方案的失败（A3）和四条具体原因（A4）；「旁听者的插话」原文是「塞小纸条」（A2） | keep，补全并更正 |
| 现稿遗漏 | 离线复盘回改实时 harness（A8）；流式 STT 的切分错误（C1–C5）；音频模式测试（C6） | 新增 |
