from datetime import date
from memory import add_meeting, load_memory
from extract import extract_meeting
from hs import retain_meeting


def read_notes():
    print("Paste or type your notes. Press Enter on an empty line when finished.")
    lines = []
    while True:
        line = input()
        if not line.strip():
            break
        lines.append(line)
    return " ".join(lines)


def to_promises(items):
    return [{"text": t, "done": False} for t in items]


def capture_meeting():
    name = input("Contact name: ").strip()
    if not name:
        print("No name entered. Cancelled.")
        return

    meeting_date = input("Date (YYYY-MM-DD, or Enter for today): ").strip()
    if not meeting_date:
        meeting_date = str(date.today())

    notes = read_notes()
    if not notes:
        print("No notes entered. Cancelled.")
        return

    print("\nReading your notes...")
    try:
        result = extract_meeting(notes)
    except Exception as e:
        print(f"Sorry, the AI could not read the notes: {e}")
        return

    print("\nHere is what I understood:")
    print("Summary:", result["summary"])
    print("You promised:", result["you_promised"])
    print("They promised:", result["they_promised"])

    ok = input("\nSave this? (y/n): ").strip().lower()
    if ok != "y":
        print("Not saved.")
        return

    # Local copy (used for the "mark as done" list)
    add_meeting(name, {
        "date": meeting_date,
        "summary": result["summary"],
        "you_promised": to_promises(result["you_promised"]),
        "they_promised": to_promises(result["they_promised"]),
    })

    # Hindsight memory
    try:
        retain_meeting(name, meeting_date, result["summary"],
                       result["you_promised"], result["they_promised"])
        print(f"Saved meeting with {name} (stored in Hindsight memory).")
    except Exception as e:
        print(f"Saved locally, but Hindsight failed: {e}")


def list_contacts():
    data = load_memory()
    if not data:
        print("No contacts yet.")
        return
    for name, info in data.items():
        print(f"- {name} ({len(info['meetings'])} meeting(s))")