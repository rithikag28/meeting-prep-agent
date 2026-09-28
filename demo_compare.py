from ai import generate
from brief import make_brief


def brief_without_memory(name):
    prompt = f"""I have a meeting with {name} soon. Write a short meeting-prep brief with these
sections: Last meeting / Missed follow-ups / Still open / Talking points.
You have no records of any past interaction with {name}. Do not invent any
details. If you do not know something, say so plainly."""
    return generate(prompt)


name = input("Contact to demo (e.g. Meera Iyer): ").strip()

print("\n" + "=" * 60)
print("BEFORE: an AI assistant WITHOUT memory")
print("=" * 60 + "\n")
print(brief_without_memory(name))

input("\n\nPress Enter to see the same request WITH Hindsight memory...")

print("\n" + "=" * 60)
print("AFTER: the same request WITH Hindsight memory")
print("=" * 60 + "\n")
print(make_brief(name))