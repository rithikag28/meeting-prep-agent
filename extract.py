import json
from ai import generate


def extract_meeting(raw_notes):
    """Turn messy meeting notes into a structured dict."""
    prompt = f"""You are a meeting-notes assistant.
Read the notes below and return JSON with exactly these keys:
- "summary": a 1-2 sentence summary of the meeting
- "you_promised": a list of things the note-taker (the user) committed to do
- "they_promised": a list of things the other person committed to do

If there are no promises for a category, use an empty list.

Notes:
{raw_notes}
"""
    text = generate(prompt, json_mode=True)
    return json.loads(text)