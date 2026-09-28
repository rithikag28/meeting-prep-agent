import json
import os

FILE = "memory.json"


def _normalize(data):
    """Convert old text promises into {'text':..., 'done':...} form."""
    for contact in data.values():
        for m in contact["meetings"]:
            for side in ("you_promised", "they_promised"):
                fixed = []
                for item in m.get(side, []):
                    if isinstance(item, str):
                        fixed.append({"text": item, "done": False})
                    else:
                        fixed.append(item)
                m[side] = fixed
    return data


def load_memory():
    if not os.path.exists(FILE):
        return {}
    with open(FILE, "r") as f:
        return _normalize(json.load(f))


def save_memory(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)


def find_contact(name, data):
    """Find a contact ignoring upper/lower case."""
    for key in data:
        if key.lower() == name.strip().lower():
            return key
    return None


def add_meeting(contact_name, meeting):
    data = load_memory()
    key = find_contact(contact_name, data) or contact_name.strip()
    if key not in data:
        data[key] = {"meetings": []}
    data[key]["meetings"].append(meeting)
    save_memory(data)


def get_open_promises(name):
    """Return (contact_key, list of promises not yet done)."""
    data = load_memory()
    key = find_contact(name, data)
    if key is None:
        return None, []
    items = []
    for mi, m in enumerate(data[key]["meetings"]):
        for side in ("you_promised", "they_promised"):
            for pi, p in enumerate(m[side]):
                if not p["done"]:
                    items.append({
                        "meeting": mi, "side": side, "index": pi,
                        "text": p["text"], "date": m["date"],
                    })
    return key, items


def mark_done(key, item):
    data = load_memory()
    data[key]["meetings"][item["meeting"]][item["side"]][item["index"]]["done"] = True
    save_memory(data)