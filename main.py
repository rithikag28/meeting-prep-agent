from capture import capture_meeting, list_contacts
from brief import make_brief
from memory import get_open_promises, mark_done
from hs import retain_preference, retain_done


def get_brief():
    name = input("Who are you meeting? ").strip()
    print("\nPreparing your brief...\n")
    print(make_brief(name))

    print()
    feedback = input("Any feedback on this brief? (Enter to skip): ").strip()
    if feedback:
        retain_preference(feedback)
        print("Got it, I'll remember that next time.")


def mark_promise_done():
    name = input("Contact name: ").strip()
    key, items = get_open_promises(name)
    if key is None:
        print(f"No records for '{name}'.")
        return
    if not items:
        print("No open promises. Everything is done!")
        return

    for i, it in enumerate(items, 1):
        who = "You" if it["side"] == "you_promised" else "They"
        print(f"{i}. [{it['date']}] {who}: {it['text']}")

    choice = input("Number to mark as done (Enter to cancel): ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(items)):
        print("Cancelled.")
        return

    item = items[int(choice) - 1]
    mark_done(key, item)
    try:
        retain_done(key, item["text"], item["side"])
    except Exception as e:
        print(f"Marked locally, but Hindsight failed: {e}")
    print("Marked as done.")


def menu():
    while True:
        print("\n=== Meeting Prep Agent (Hindsight memory) ===")
        print("1. Log a meeting (paste notes)")
        print("2. Get a brief before a meeting")
        print("3. Mark a promise as done")
        print("4. List my contacts")
        print("5. Quit")
        choice = input("Choose 1-5: ").strip()

        print()
        if choice == "1":
            capture_meeting()
        elif choice == "2":
            get_brief()
        elif choice == "3":
            mark_promise_done()
        elif choice == "4":
            list_contacts()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Please type a number from 1 to 5.")


menu()