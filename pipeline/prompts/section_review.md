You are reviewing and rewriting one section of a short report on AI Engineer Shanghai 2026 (Nov 5–6, 2026; 53 talks). The reader is Ricky, an experienced observer who works in the content industry. Write the output in Chinese, keeping technical terms and names in English.

## Your section
{section_brief}

Current text of the section: `data/05_synthesis/sections/{sid}_current.md`

## Sources (project root <project_root>)
- `data/03_clean/*.md`: proofread transcripts of all 53 talks. Paragraphs end with `[seg A–B]`. **This is the ground truth.**
- `data/05_synthesis/_input/all_talks.json`: per-talk summaries. Use it only to find which talks are relevant. Don't quote it.
- `data/01_talks.csv`: talk_id → speaker, org, title.
- `data/05_synthesis/substance_filter.csv`: talks Ricky judged to be mostly product promotion. Don't build insights on their claims, but you may use them as market facts (who sells what, which problem they say they solve).
- `data/05_synthesis/exhibitors.csv`: expo exhibitors who did not speak, from their websites. Mark anything taken from it as 展商.

## What to do
1. Search every transcript for material relevant to your section. Use the summaries to shortlist talks, then grep the transcripts for related terms in both Chinese and English. Read the relevant passages in full. Don't limit yourself to the talks the current text cites.
2. Write `data/05_synthesis/sections/{sid}_evidence.md`. List every candidate point with talk_id, the verbatim quote(s) from the transcript, and seg range, plus your verdict on each: **keep** (solid and valuable), **merge** (into which point), or **drop** (with the reason: not supported by the source, obvious or common knowledge, low value, PR only, or misattributed).
3. Write `data/05_synthesis/sections/{sid}_revised.md`, the rewritten section:
   - Use a pyramid structure: one sentence stating the section's main finding, then 2–4 supporting points, each with talk ids like [d1m05]. The supporting points should not overlap. Readers should see why each point belongs under the main finding.
   - Keep only points that are solid in the source and valuable to an experienced reader. Fewer is better. Don't aim for coverage.
   - Every claim must be traceable to a quote in your evidence file. Mark your own inferences with （推断）.
   - Tables are fine where they make a comparison clearer.

## Style rules (strict)
- Don't use contrast rhetoric: 不是…而是, 与其…不如, 看似…实则, 这不是…这是. State the point directly.
- Don't use filler transitions, restatement, or padding. Use short declarative sentences.
- Don't cite exact numbers. All numbers come from speech recognition and are unverified. If a metric matters, say which metric the speaker tracks.
- Don't present a generic or well-known point as an insight.

Final reply (under 150 words): the main finding sentence, what you kept, merged and dropped versus the current text, and anything important you found in the transcripts that the current text missed.
