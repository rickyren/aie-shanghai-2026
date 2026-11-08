You are an industry analyst tagging one talk from AI Engineer Shanghai 2026 (Nov 5–6, 2026). The output feeds an industry-trend report for a reader who works in the content industry (video, editing, creators, content platforms). Do NOT open files other than the inputs below, and do not use web search: everything must come from the talk.

Inputs (project root <project_root>):
- `data/03_clean/{file_id}.md` — proofread transcript. Paragraphs end with `[seg A–B]` (source line ranges).
- `data/03_clean/{file_id}.notes.json` — speaker facts and corrections from proofreading.
- `data/03_clean/_input/{file_id}.meta.json` — agenda metadata (title, speakers, orgs, format).
- `pipeline/schemas/talk_analysis.json` — the output shape and the allowed enum codes with their meaning. Read it carefully.

Write `data/04_analysis/{file_id}.json` following `shape` exactly, using only the enum codes listed under `enums`.

Rules:
- Analysis fields are in Chinese. Keep names, products and technical terms in their usual form. `quote` fields are verbatim substrings of the clean transcript (original language), short (one or two sentences), and `seg` is the range of the paragraph they come from.
- Be specific and concrete: name the technique, number, customer or product. Avoid generic statements like "AI 很重要". If the talk has no content for a list field, use an empty list — do not pad.
- key_claims: 3–6 of the most important, non-obvious claims. practices: only for things the speaker actually did or observed, with outcome. predictions: only explicit forward-looking statements.
- signals: be thorough about `data` signals — what data is being collected, produced, bought or sold (RL environments, agent trajectories, human demonstrations, domain data, hiring experts to produce data, etc.). These matter most to the reader.
- org.value_chain_layer: classify the speaker's organization by what it sells/does, not by the talk topic. A bank or trading firm using AI is `ai_adopter`. For panels of investors use `capital_community`; for multi-org panels pick the dominant type and explain in `layer_rationale`.
- scores: info_density = how much concrete, reusable information; novelty = how new to an informed AI practitioner in late 2026; pr_level = how much of the talk is promoting the speaker's own product (5 = mostly a pitch).
- content_industry_note: only if there is a real, specific implication for video/editing/creators/content platforms; otherwise empty string.

Before finishing, validate with a short `python3 -I` script (in your own `mktemp -d` directory; other agents share /tmp): JSON parses, all enum fields use allowed codes, every `quote` is a substring of the clean transcript (ignore whitespace differences), and every `seg` lies within the transcript's ranges. Fix any failures.

Final reply (under 80 words): layer, talk_type, core_message, and the validation result.
