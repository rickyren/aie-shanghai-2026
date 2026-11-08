"""Shared Jev (TypeSafe System One) setup: key lookup, questions, context window, batch classify."""
import asyncio
import os
import subprocess
import sys
import time

from typesafe_sdk import AsyncTypeSafeClient, Choice, Noul

CONTEXT = 4
CONCURRENCY = 8
TYPES = ["talk", "host", "logistics", "noise"]

QUESTIONS = {
    "segment_type": Choice(
        instructions=(
            "This is a live conference transcript (Chinese/English mixed, produced by speech recognition). "
            "Classify ONLY the `target` segment; `before`/`after` are context."
        ),
        criteria={
            "talk": "Content delivered by an invited speaker or panelist: their talk, own greeting or "
                    "self-introduction, closing thanks of their own talk, Q&A, and panel moderator questions. "
                    "Includes short fillers or broken fragments in the middle of a talk.",
            "host": "The event emcee or organizer speaking between talks: introducing the next speaker or "
                    "topic, thanking the previous speaker, asking for applause, conference opening/closing remarks.",
            "logistics": "Housekeeping and stage setup: take your seats, breaks, lunch, schedule notices, "
                         "slides/mic/AV checks.",
            "noise": "Unintelligible speech-recognition garbage that fits none of the above.",
        },
    ),
    "talk_start": Noul(
        instructions=(
            "Is the `target` segment the moment an invited speaker (or a panel) starts their own session, "
            "e.g. their first greeting or self-introduction right after being introduced?"
        ),
        criteria={"true": "The target opens a new speaker's session.",
                  "false": "Anything else, including the emcee's introduction itself and mid-talk content."},
    ),
}


def api_key():
    key = os.environ.get("TYPESAFE_API_KEY")
    if key:
        return key
    try:
        return subprocess.run(["security", "find-generic-password", "-s", "TYPESAFE_API_KEY", "-w"],
                              capture_output=True, text=True, check=True).stdout.strip()
    except subprocess.CalledProcessError:
        sys.exit("TYPESAFE_API_KEY not found in env or Keychain")


def build_state(segs, topic, order):
    """segs: {seg_id: row}. Context is taken by message_order within the same topic."""
    def text(o):
        r = segs.get(f"{topic}:{o}")
        return r["source_text"] if r else None
    before = [t for o in range(order - CONTEXT, order) if (t := text(o))]
    after = [t for o in range(order + 1, order + CONTEXT + 1) if (t := text(o))]
    return {"before": before, "target": text(order), "after": after}


async def classify(items, segs, key):
    """items: dicts with seg_id. Returns items enriched with Jev answers (or an `error`)."""
    sem = asyncio.Semaphore(CONCURRENCY)
    async with AsyncTypeSafeClient(api_key=key, model="jev-latest") as client:
        async def one(s):
            topic, order = s["seg_id"].split(":")
            state = build_state(segs, topic, int(order))
            async with sem:
                t0 = time.perf_counter()
                try:
                    resp = await client.system_one(state=state, questions=QUESTIONS)
                except Exception as e:  # keep going; surface the error downstream
                    return {**s, "state": state, "error": f"{type(e).__name__}: {e}"}
                ms = (time.perf_counter() - t0) * 1000
            st, ts = resp.answers["segment_type"], resp.answers["talk_start"]
            return {**s, "state": state, "pred_type": st.choice, "confidence": st.confidence,
                    "probs": dict(st.probabilities), "start_p": ts.noul, "latency_ms": round(ms),
                    "in_tok": resp.usage.input_tokens, "model": resp.model}
        return await asyncio.gather(*(one(s) for s in items))
