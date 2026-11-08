You are proofreading one conference talk transcribed live by speech recognition (AI Engineer Shanghai 2026). Do NOT open any file other than the inputs below.

Inputs (project root <project_root>):
- `{input_dir}/{file_id}.txt` — the talk's content lines only (host transitions and logistics are already removed). Tab-separated: `order <TAB> text`. `order` numbers may skip where non-talk lines were removed.
- `{input_dir}/{file_id}.meta.json` — agenda metadata: speakers, organizations, title, format (talk / panel / rapid_fire / opening), moderator, and a glossary of names and terms from the whole conference program.

## Task 1 — clean transcript (清稿)
Rewrite the talk into readable, faithful text in its ORIGINAL language (Chinese stays Chinese, English stays English; mixed-language sentences keep their mix — keep English technical terms as spoken).
- Fix speech-recognition errors: misheard names, company/product names, technical terms, homophones (e.g. 限量数据库 → 向量数据库). Use the glossary, the agenda, and the surrounding context. Only fix what you are confident about.
- Remove fillers and disfluencies (呃、啊、就是就是、um, uh, you know, repeated false starts), stage chatter that slipped in (mic checks, "can you see my screen", clicker problems), and pure repetitions.
- Do NOT summarize, shorten arguments, merge separate points, add explanations, or add anything not said. Keep every substantive claim, example, number, product name, and opinion. Keep the speaker's voice and first person.
- Group into natural paragraphs (typically 3–10 source lines each). After each paragraph put its source range as `[seg A–B]` using the first and last `order` it covers.
- Where the source is garbled and you cannot recover the meaning, keep your best reading and mark it `〔?〕`; if a passage is unrecoverable, write `〔无法辨识〕` / `〔unintelligible〕`.
- Use section headings (`##`) only where the speaker clearly moves to a new part; don't invent structure.
- Panels / multi-speaker: start each turn with the speaker's name in bold (e.g. `**戴雨森**：`). Identify speakers from self-introductions, the moderator's addressing, and content. If a turn's speaker is uncertain, write `**？（可能是 戴雨森）**：`.
- Slides the speaker reads out or demo prompts are kept, but you may set them as quotes.

## Task 1b — verify uncertain proper nouns with web search
After the glossary and context, some names may still be uncertain: companies, products, models, people, papers, open-source projects, Chinese name characters (e.g. 王怀 vs 王淮), or corrections that rely on outside knowledge (e.g. "training firm" → "trading firm" because Optiver is a trading firm). For these, use WebSearch (at most ~10 searches per talk; batch several names into one query when possible) to confirm the correct spelling.
- Search is ONLY for resolving what the speaker actually said. Never add facts, explanations, or links from the web into the clean transcript.
- A name counts as verified only if a search result clearly matches the context (same company/field/person). Otherwise keep `〔?〕`.
- Record every lookup in `verified` in the notes file (see below), including failed ones.

## Task 2 — speaker facts (only what is said in this transcript)
For each person who speaks as a guest (and the moderator for panels): corrected name, organization, role/title, and background as they describe it (previous companies, what they built, investment focus...). Give the `order` where it is said. Background must come from the transcript only; web search may be used only to confirm the spelling of the name and organization.

## Output
Write two files:
1. `{output_dir}/{file_id}.md`:
```
---
talk_id: {talk_id}
title: <agenda title, or the actual topic if clearly different>
speakers: <corrected names, comma-separated>
orgs: <orgs>
language: <zh|en|mixed>
source_segments: <first>–<last>
---
<clean transcript>
```
2. `{output_dir}/{file_id}.notes.json`:
`{"talk_id": "...", "speakers": [{"name": "...", "name_as_heard": ["..."], "org": "...", "role": "...", "background": "...", "evidence_orders": [..]}], "corrections": [{"from": "<as heard>", "to": "<corrected>", "count": <approx times>, "confidence": "high|medium"}], "removed_non_content": [{"orders": "A–B", "what": "<e.g. clicker problem>"}], "uncertain": [{"orders": "A–B", "issue": "..."}], "verified": [{"as_heard": "...", "resolved_to": "<name, or null if not resolved>", "evidence": "<url + a few words on why it matches>", "orders": "A–B"}], "actual_topic_note": "<only if the talk differs from the agenda title>"}`

List the 10–30 most important corrections (names, terms, numbers), not every filler removal.

Before finishing, check with a short `python3 -I` script (create it in your own fresh directory from `mktemp -d`; other agents run in parallel and share /tmp) that: every `[seg A–B]` range is within the input, ranges are in ascending order, and together they cover the input lines except ones you intentionally removed (list those in `removed_non_content`). Report the clean/raw character ratio.

Final reply (under 120 words): character ratio, number of paragraphs, number of 〔?〕, number of web-verified names, and the most significant corrections.
