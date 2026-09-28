import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

BANK = "meeting-prep"


def _with_client(fn):
    """Run fn(client) in its own thread with a fresh client.
    This avoids 'event loop is already running' errors inside Streamlit."""

    def worker():
        c = Hindsight(
            base_url=os.getenv("HINDSIGHT_BASE_URL"),
            api_key=os.getenv("HINDSIGHT_API_KEY"),
        )
        try:
            return fn(c)
        finally:
            try:
                c.close()
            except Exception:
                pass

    with ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(worker).result()


def retain_meeting(name, meeting_date, summary, you_promised, they_promised):
    """Store one meeting in Hindsight memory."""
    content = f"Meeting with {name} on {meeting_date}. Summary: {summary}. "
    if you_promised:
        content += "I (the user) promised: " + "; ".join(you_promised) + ". "
    if they_promised:
        content += f"{name} promised: " + "; ".join(they_promised) + ". "

    try:
        ts = datetime.strptime(meeting_date, "%Y-%m-%d")
    except ValueError:
        ts = datetime.now()

    _with_client(lambda c: c.retain(
        bank_id=BANK,
        content=content,
        context=f"meeting with {name}",
        timestamp=ts,
    ))


def retain_done(name, promise_text, side):
    """Store that a promise was completed."""
    who = "the user" if side == "you_promised" else name
    _with_client(lambda c: c.retain(
        bank_id=BANK,
        content=f"Completion status: {who} has COMPLETED this promise involving {name}: "
                f"'{promise_text}'. Status: DONE.",
        context=f"promise status for {name}",
    ))


def retain_preference(text):
    """Store how the user likes their briefs."""
    _with_client(lambda c: c.retain(
        bank_id=BANK,
        content=f"The user's preference for meeting briefs: {text}",
        context="user preference",
    ))


def _recall_many(queries, tokens=3000):
    def run(c):
        out = []
        for q in queries:
            res = c.recall(bank_id=BANK, query=q, max_tokens=tokens, budget="high")
            out.append([r.text for r in res.results])
        return out
    return _with_client(run)


def recall_contact(name):
    """Recall meetings, both sides' promises, and completions for one contact."""
    queries = [
        f"Every meeting with {name}: dates, what was discussed, and their concerns",
        f"Everything the user promised {name}, with deadlines",
        f"Everything {name} promised the user, with deadlines",
        f"Promises involving {name} that have been completed or marked DONE",
    ]
    seen, merged = set(), []
    for texts in _recall_many(queries):
        for text in texts:
            if text not in seen:
                seen.add(text)
                merged.append(text)
    return merged


def recall_preferences():
    """Get the user's remembered brief-style preferences."""
    return _recall_many(
        ["How does the user like their meeting briefs written and formatted?"], 1024
    )[0]