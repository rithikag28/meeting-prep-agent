from memory import load_memory, add_meeting
from hs import retain_meeting, retain_done


def P(text, done=False):
    return {"text": text, "done": done}


DEMO = {
    "Meera Iyer": [
        {"date": "2026-08-04",
         "summary": "Intro call with Meera (VP Operations, Northwind Logistics). Last-mile delivery delays across 3 warehouses. Open to a pilot of route-optimization software. Budget cycle closes end of September. Worried about integrating with their legacy system.",
         "you": [P("Send route-optimization case study by Aug 7", True), P("Share pricing overview by Aug 14", True)],
         "they": [P("Introduce IT lead Karthik Rao by Aug 11", True)]},
        {"date": "2026-08-13",
         "summary": "Discovery call with Karthik Rao. Legacy system exposes a REST API. Main worry is data security and India-region hosting.",
         "you": [P("Send security whitepaper and SOC 2 summary by Aug 18", False)],
         "they": [P("Share 3 months of sample delivery data by Aug 20", True)]},
        {"date": "2026-08-27",
         "summary": "Pilot scoping. Agreed a 6-week pilot at the Hyderabad warehouse. Meera prefers short bullet updates and dislikes long decks. Still waiting on the security documents and mildly frustrated.",
         "you": [P("Send pilot proposal with pricing by Sept 3", True), P("Resend security whitepaper and SOC 2 summary", False)],
         "they": [P("Get budget approval from CFO Anil Shah by Sept 10", False)]},
        {"date": "2026-09-10",
         "summary": "CFO approval delayed by a week. Karthik set up the sandbox. Meera asked for an ROI estimate.",
         "you": [P("Send ROI estimate by Sept 15", False)],
         "they": [P("Confirm CFO approval by Sept 17", False), P("Provide sandbox credentials", True)]},
        {"date": "2026-09-22",
         "summary": "CFO still has not approved. Meera wants a revised pricing option with a volume discount before she takes it back. Target pilot start is Oct 5.",
         "you": [P("Send revised pricing with 8% volume discount by Sept 25", False)],
         "they": [P("Sign pilot agreement by Oct 1", False)]},
    ],
    "Daniel Okafor": [
        {"date": "2026-08-06",
         "summary": "First call with Daniel (CTO, Brightpath Health). He wants to cut patient no-show rates, currently 18% across 12 clinics. HIPAA compliance is mandatory.",
         "you": [P("Send HIPAA compliance overview by Aug 10", True)],
         "they": [P("Share current no-show data by Aug 13", True)]},
        {"date": "2026-08-20",
         "summary": "Reviewed his data and ran a demo. Daniel liked the automated reminders but is skeptical about prediction accuracy.",
         "you": [P("Send accuracy benchmark report by Aug 27", False)],
         "they": [P("Introduce compliance officer Ritu Bansal by Aug 25", True)]},
        {"date": "2026-09-08",
         "summary": "Ritu raised a data residency question. Daniel prefers detailed written follow-ups after every call.",
         "you": [P("Send written answer on data residency by Sept 12", True)],
         "they": [P("Decide on a 2-clinic pilot by Sept 20", False)]},
        {"date": "2026-09-23",
         "summary": "Daniel is undecided and comparing us with a competitor called Clinicly. He wants per-clinic pilot pricing.",
         "you": [P("Send per-clinic pricing by Sept 28", False)],
         "they": [P("Share his competitor evaluation criteria", False)]},
    ],
    "Sofia Martins": [
        {"date": "2026-09-01",
         "summary": "Intro with Sofia (Procurement Lead, Lumen Retail). She is consolidating vendors and needs 3 quotes. Standard payment terms are net-60.",
         "you": [P("Send company registration and vendor forms by Sept 5", True)],
         "they": [P("Share vendor evaluation scorecard by Sept 8", True)]},
        {"date": "2026-09-15",
         "summary": "Reviewed her scorecard. Our pricing is 12% above the incumbent. She asked for volume tiers.",
         "you": [P("Send revised quote with volume tiers by Sept 20", False)],
         "they": [P("Confirm decision timeline", False)]},
        {"date": "2026-09-24",
         "summary": "Sofia is annoyed the revised quote has not arrived. The decision committee meets Oct 8.",
         "you": [P("Send revised quote by Sept 26", False), P("Send three customer references", False)],
         "they": [P("Send committee agenda by Oct 1", False)]},
    ],
}


existing = load_memory()

for name, meetings in DEMO.items():
    if name in existing:
        print(f"Skipping {name} (already exists)")
        continue

    # 1. Store in Hindsight memory
    for m in meetings:
        retain_meeting(name, m["date"], m["summary"],
                       [p["text"] for p in m["you"]],
                       [p["text"] for p in m["they"]])
        for side, key in (("you_promised", "you"), ("they_promised", "they")):
            for p in m[key]:
                if p["done"]:
                    retain_done(name, p["text"], side)
        print(f"  Stored in Hindsight: {name} on {m['date']}")

    # 2. Store locally (for the mark-as-done menu)
    for m in meetings:
        add_meeting(name, {
            "date": m["date"],
            "summary": m["summary"],
            "you_promised": m["you"],
            "they_promised": m["they"],
        })
    print(f"Done: {name}\n")

print("All demo data loaded.")