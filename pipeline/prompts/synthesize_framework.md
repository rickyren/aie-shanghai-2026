You are a senior industry analyst. Your job: build the overall analytical framework for a report on AI Engineer Shanghai 2026 (Nov 5–6, 2026, Shanghai; 53 sessions on two stages), from per-talk analyses that have already been produced. This is the step where cross-talk patterns are found, so read everything before deciding on any structure. Write in Chinese (keep names and technical terms in their usual form).

## The reader and what they want
Ricky works in the content industry (video, editing, creators, content platforms) and attended the conference. He wants a shareable piece that explains the current state of the AI industry as seen through this event:
1. **Industry landscape** — which companies were there, what each actually does / sells and to whom, and where it sits in the value chain. This is the most important part and must be built bottom-up from the talks, not from a textbook stack.
2. **Trend judgments per theme** — e.g. for agent harness: what is hot now, what problems people hit, what new approaches are emerging; similar for every theme that genuinely emerged.
3. **Data market** — what kinds of data are being produced / bought / sold now (lots of RL data), and what might be sold next. Ricky's own field observation: at the event someone was hiring video editors, which suggests data on AI operating editing project files may appear and could raise base models' native editing ability. Treat this as his observation, not a transcript fact.
4. **Application layer** — which application directions already show real opportunity, application-layer trends, contrasted with what the investors said.
5. **Implications for the content industry.**

Ricky's field impression: very few companies there actually train models (and those that do are mid/long-tail, e.g. StepFun); most either serve models (infra, data) or build applications. Test this against the data; don't just echo it.

## Ground rules
- Qualitative over quantitative. All numbers come from live speech recognition and are unverified (no slides/video yet). Do not build any conclusion on an exact value; when a metric matters, say which metric players track and what that reveals.
- Drop consensus. Skip anything an informed AI practitioner already takes for granted in late 2026, unless the event adds a genuinely new angle or evidence.
- Every claim about the industry must cite the talks it rests on, as `[talk_id]` (e.g. `[d1m05][d2m10]`). Distinguish what speakers said from your own inference: mark inferences with "（推断）".
- Be honest about sampling: this is one conference's speaker lineup, shaped by sponsors and the organisers' choices, not the whole market. Note where that biases the picture.
- Prefer sharp, falsifiable statements over balanced mush. If speakers disagree, show the disagreement.

## Inputs (project root <project_root>)
- `data/05_synthesis/_input/all_talks.json` — all 53 per-talk analyses in agenda order. Fields: speaker intent, skeleton, core_message, frameworks the speaker proposed, offerings, why_needed (positioning vs alternatives), problem_approach, non_consensus (typed), signals (data_signal / market_pattern / metric_focus / launch), value_chain_layer (a first-pass label — see below), position, target_customer, trend_categories, novelty, pr_level, content_industry_note. READ ALL OF IT.
- `pipeline/schemas/talk_analysis_v3.json` — meaning of the codes.
- `data/02_speakers.csv` — speakers, orgs, roles, self-described background.
- `analysis/trend-categories-draft.md` — Ricky's earlier draft of 10 themes. Revise it bottom-up.
- `data/03_clean/<file_id>.md` — full proofread transcripts. Consult them when a per-talk analysis is ambiguous or when you need to check a cross-talk claim. You don't need to read all of them.

Known problem with the first-pass `value_chain_layer`: some talks were labelled by the topic of the talk instead of by what the organisation does (e.g. MiniMax labelled agent infrastructure because the talk was about harness; Manus labelled "AI adopter" because the talk was about internal practice; OpenClaw, Langfuse also questionable). For the landscape, classify organisations by what they do/sell; keep "what the talk was about" separate. You may also redesign the layer taxonomy itself if the evidence suggests a better cut (e.g. a separate layer for agent commerce/identity/trust, or for "data for model labs"). Explain your taxonomy choice briefly.

## Outputs
1. `data/05_synthesis/org_calibration.csv` with columns:
   `org,talk_ids,final_layer,sub_position,what_they_sell,sells_to,talk_topic_layer,changed_from_first_pass,reason`
   One row per organisation (panels: one row per participating org). `final_layer` uses your (possibly revised) taxonomy.
2. `data/05_synthesis/framework.md` — the framework, structured as:
   - `# 0. 一页结论` — 5–8 headline judgments, each one sentence plus citations.
   - `# 1. 产业 Landscape` — your taxonomy; per layer: who is there, what they sell, to whom; then the cross-layer patterns (where the crowd is, what's thin or missing, who sells to whom / value flows, which layers are being squeezed or absorbed by model labs, interesting adjacency moves such as eval platforms turning into data vendors). Include a compact text map of the stack.
   - `# 2. 主题与趋势` — the revised theme list (say what you merged, split, added, dropped vs the draft, and why). Per theme: 热点 / 卡点 / 新做法 / 分歧, with citations. Only themes with real substance.
   - `# 3. 数据市场` — data types being produced/traded now, by whom, for whom; the mechanisms (eval → RL environments, consumer product → trajectories, field collection, etc.); what might be traded next, with Ricky's editing-data hypothesis assessed against the evidence.
   - `# 4. 应用层` — directions with evidence of traction vs hype, patterns, and the investors' views side by side with what builders said.
   - `# 5. 对内容行业的启示` — specific, actionable implications; separate near-term from speculative.
   - `# 6. 局限与待核实` — sampling bias, unverifiable numbers, gaps (e.g. talks with missing audio), open questions for when slides/videos arrive.
   - `# 附：讲者金句候选` — 8–12 short verbatim quotes (from the transcripts) that crystallise the judgments, with talk ids.

Aim for depth over length: the framework should be readable in about 20 minutes. Before finishing, re-check that every talk id you cite exists and that each headline judgment is supported by at least two talks or explicitly marked as resting on one.

Final reply (under 200 words): your layer taxonomy in one line, the 5–8 headline judgments, and anything you were unsure about.
