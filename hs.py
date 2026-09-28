import os
import atexit
from datetime import datetime
from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

BANK = "meeting-prep"

client = Hindsight(
    base_url=os.getenv("HINDSIGHT_BASE_URL"),
    api_key=os.getenv("HINDSIGHT_API_KEY"),
)


def _close():
    try:
        client.close()
    except Exception:
        pass


atexit.register(_close)


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

    client.retain(
        bank_id=BANK,
        content=content,
        context=f"meeting with {name}",
        timestamp=ts,
    )


def retain_done(name, promise_text, side):
    """Store that a promise was completed (no date text, to avoid confusing meeting dates)."""
    who = "the user" if side == "you_promised" else name
    client.retain(
        bank_id=BANK,
        content=f"Completion status: {who} has COMPLETED this promise involving {name}: "
                f"'{promise_text}'. Status: DONE.",
        context=f"promise status for {name}",
    )


def retain_preference(text):
    """Store how the user likes their briefs."""
    client.retain(
        bank_id=BANK,
        content=f"The user's preference for meeting briefs: {text}",
        context="user preference",
    )


def _recall(query, tokens=3000):
    res = client.recall(bank_id=BANK, query=query, max_tokens=tokens, budget="high")
    return [r.text for r in res.results]


def recall_contact(name):
    """Recall meetings, both sides' promises, and completions for one contact."""
    queries = [
        f"Every meeting with {name}: dates, what was discussed, and their concerns",
        f"Everything the user promised {name}, with deadlines",
        f"Everything {name} promised the user, with deadlines",
        f"Promises involving {name} that have been completed or marked DONE",
    ]
    seen, merged = set(), []
    for q in queries:
        for text in _recall(q):
            if text not in seen:
                seen.add(text)
                merged.append(text)
    return merged


def recall_preferences():
    """Get the user's remembered brief-style preferences."""
    return _recall("How does the user like their meeting briefs written and formatted?", 1024)