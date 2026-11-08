You are segmenting a live-conference speech-recognition transcript (AI Engineer Shanghai 2026). Do NOT open any file other than the two inputs below.

Inputs (project root <project_root>):
- `{window_dir}/window.txt` — tab-separated lines: `order <TAB> time(HH:MM:SS, Shanghai) <TAB> text`. Chinese/English mixed; ASR errors are common (names and companies are often misrecognized as sound-alike words). Timestamps are mostly reliable but some are out of order or were edited later; `order` is authoritative.
- `{window_dir}/agenda.csv` — ALL scheduled sessions of this stage/half-day. This window ({topic_id}:{from}–{to}) covers only part of it. The real running order may differ from the agenda, speakers can be swapped, and there may be talks that are not on the agenda at all. The window may start or end in the middle of a talk.

Task: label EVERY order from {from} to {to} with exactly one type, as contiguous spans:
- `talk`: content from an invited speaker or panelist — their greeting/self-introduction, the talk itself, their own closing thanks, Q&A. In a panel, the moderator's questions and remarks are `talk` too. Short fillers or broken fragments in the middle of a talk are `talk`. If the window starts mid-talk, those lines are `talk` of the session you infer from content.
- `host`: the emcee/organizer outside a session — thanking the previous speaker, introducing the next speaker/topic, applause cues, "let's get started", conference opening/closing speeches by organizers.
- `logistics`: breaks, lunch, "take your seats", schedule notices, stage/AV/slides/mic setup chatter.
- `noise`: unintelligible garbage that fits nothing else (rare).
If one line mixes host and talk content (e.g. the emcee's intro and the speaker's first words were recognized as one line), label it by what dominates and mention the order in notes.

Every `talk` span carries a `session_id`: the agenda session_id it belongs to, identified from the host's introduction, the speaker's self-introduction and the content — not from position alone. A talk that is not on the agenda gets `offagenda:<speaker name or org>`. The goal downstream is to keep ONLY clean guest content, so be precise at boundaries: read the lines around every transition carefully.

Read the whole window (in chunks). Then write `{window_dir}/llm_labels.json` with exactly this shape:
{"method": "llm_subagent", "window": "{window_id}", "spans": [{"from": <order>, "to": <order>, "type": "talk|host|logistics|noise", "session_id": "<id; only for talk>"}...], "sessions_found": [{"session_id": "...", "speaker_as_heard": "...", "evidence_order": <order of the intro/self-intro line>}], "notes": "<uncertain boundaries, mixed lines, agenda deviations, with order numbers>"}
Spans must be contiguous, non-overlapping, sorted, and cover {from}..{to} completely (some order numbers may be missing in the file — spans just need to cover every order that exists). Validate with a tiny `python3 -I` check before finishing. Do not modify any other file.

Final reply (under 150 words): the sessions found in order with their spans, plus agenda deviations and uncertainties.
