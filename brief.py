import re
from difflib import SequenceMatcher
from datetime import date
from ai import generate
from hs import recall_contact, recall_preferences
from memory import load_memory, find_contact

MONTHS = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
          "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}


def parse_deadline(text):
    """Find 'by Sept 3' style deadlines in a promise. Returns a date or None."""
    m = re.search(r"\bby\s+([A-Za-z]{3})[a-z]*\.?\s+(\d{1,2})", text)
    if not m:
        return None
    month = MONTHS.get(m.group(1).lower())
    if not month:
        return None
    try:
        return date(2026, month, int(m.group(2)))
    except ValueError:
        return None


def strip_deadline(text):
    return re.sub(r"\s+by\s+.*$", "", text).strip()


def norm_key(text):
    """Reduce a promise to its core wording."""
    t = strip_deadline(text).lower()
    t = re.sub(r"^(resend|send|share|provide)\s+", "", t)
    return t.strip()


def same_promise(a, b):
    """True if two promise wordings are clearly the same promise."""
    if not a or not b:
        return False
    if a.startswith(b) or b.startswith(a):
        return True
    return SequenceMatcher(None, a, b).ratio() >= 0.75


def build_ledger(name):
    """Return (last_date, last_summary, unique promises with latest status)."""
    data = load_memory()
    key = find_contact(name, data)
    if key is None:
        return None, None, None
    meetings = sorted(data[key]["meetings"], key=lambda m: m["date"])

    items = {}
    for m in meetings:
        for side in ("you_promised", "they_promised"):
            for p in m[side]:
                nk = norm_key(p["text"])

                # find an existing similar promise on the same side
                k = (side, nk)
                for (s, existing) in items:
                    if s == side and same_promise(existing, nk):
                        k = (s, existing)
                        break

                prev = items.get(k)
                text = p["text"]
                deadline = parse_deadline(text)
                if prev and deadline is None:      # keep the earlier deadline
                    deadline = prev["deadline"]
                items[k] = {"side": side, "text": text,
                            "deadline": deadline, "done": p["done"]}
    last = meetings[-1]
    return last["date"], last["summary"], list(items.values())


def fmt(item):
    who = "you owe" if item["side"] == "you_promised" else "they owe"
    d = f"due {item['deadline'].strftime('%b %d')}" if item["deadline"] else "no deadline"
    return f"- {strip_deadline(item['text'])} ({who}, {d})"


def make_brief(name):
    last_date, last_summary, items = build_ledger(name)
    if items is None:
        return f"I have no records for '{name}' yet."

    today = date.today()
    open_items = [i for i in items if not i["done"]]
    missed = sorted(
        [i for i in open_items if i["deadline"] and i["deadline"] < today],
        key=lambda i: i["deadline"])
    still_open = [i for i in open_items if i not in missed]

    missed_txt = "\n".join(fmt(i) for i in missed) or "- None"
    open_txt = "\n".join(fmt(i) for i in still_open) or "- None"

    memories = recall_contact(name)
    context = "\n".join(f"- {m}" for m in memories) if memories else "- (none)"
    prefs = recall_preferences()
    pref_text = "\n".join(f"- {p}" for p in prefs) if prefs else "- None yet"

    prompt = f"""You are my meeting-prep assistant. Today is {today}.
I am about to meet {name}.

LAST MEETING ({last_date}), exact notes:
{last_summary}

MISSED FOLLOW-UPS (already calculated and complete, oldest first):
{missed_txt}

STILL OPEN, NOT YET DUE:
{open_txt}

MEMORY CONTEXT (recalled across ALL my past meetings with {name}):
{context}

RULES:
1. Only about {name}. Do not invent facts, deadlines or events.
2. Last meeting: use ONLY the exact notes above. Add nothing from other meetings.
3. "What I remember about them": up to 2 bullets, ONLY things stated in the memory
   context or last meeting notes about {name}. If there is only one supported fact,
   write one bullet. Never guess or pad. No promises, no dates.
4. Copy the missed and open lists exactly. Do not add, remove, merge or re-date
   items, and do not repeat an item in both sections.
5. "(you owe)" means I have not delivered it yet. Never suggest asking them to
   confirm receipt of something I have not sent. Suggest delivering it, or
   apologising for the delay.
6. Talking points: 3 maximum, based on the missed and open items.
7. If my style preferences ask for a mood note, describe how {name} seems to feel
   (never how I feel), in one line, based on the memory context and last meeting.

Sections, in this order:
Last meeting / Mood (only if requested) / What I remember about them / Missed follow-ups / Still open / Talking points

My saved style preferences (if several conflict, obey the most recent one;
never drop items from the missed list to save space):
{pref_text}"""

    return generate(prompt)