import html
from datetime import date

import streamlit as st

from ai import generate
from extract import extract_meeting
from hs import retain_meeting, retain_preference
from memory import load_memory, add_meeting, find_contact
from brief import make_brief, build_ledger
from hs import recall_contact


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Meeting Prep Agent",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CSS
# ============================================================

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp { background-color: #f6f7fb; color: #172033; }

.block-container { max-width: 1380px; padding-top: 2.2rem; padding-bottom: 4rem; }

section[data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e7e9f2; }

.sidebar-brand { font-size: 1.35rem; font-weight: 800; color: #172033; margin-bottom: 0.15rem; }
.sidebar-subtitle { color: #7a8194; font-size: 0.82rem; margin-bottom: 1.5rem; }
.sidebar-section { font-size: 0.72rem; font-weight: 700; color: #9298a8;
    text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.5rem; }

.app-title { font-size: 2.45rem; font-weight: 800; letter-spacing: -0.04em;
    color: #172033; line-height: 1.15; }
.app-subtitle { font-size: 1rem; color: #747c91; margin-top: 0.35rem; }

.memory-status { display: inline-block; background-color: #eef2ff; border: 1px solid #d9ddff;
    color: #5146c7; padding: 0.55rem 0.9rem; border-radius: 999px;
    font-size: 0.82rem; font-weight: 700; text-align: center; }

.section-title { font-size: 1.25rem; font-weight: 700; color: #172033;
    margin-top: 1.8rem; margin-bottom: 0.85rem; letter-spacing: -0.02em; }

.contact-card { background: linear-gradient(135deg, #ffffff 0%, #f8f7ff 100%);
    border: 1px solid #e3e4f2; border-radius: 18px; padding: 1.45rem 1.6rem;
    margin: 0.4rem 0 1.4rem 0; box-shadow: 0 5px 18px rgba(45, 42, 90, 0.06); }
.contact-name { font-size: 1.5rem; font-weight: 700; color: #172033; margin-bottom: 0.3rem; }
.contact-details { color: #737b8f; font-size: 0.9rem; }

div[data-testid="stMetric"] { background-color: #ffffff; border: 1px solid #e5e7ef;
    border-radius: 16px; padding: 1rem 1.15rem; box-shadow: 0 4px 14px rgba(25, 30, 60, 0.04); }
div[data-testid="stMetricLabel"] { color: #7b8295; font-weight: 500; }
div[data-testid="stMetricValue"] { color: #172033; font-weight: 700; }

.brief-card { background-color: #ffffff; border: 1px solid #e6e8f0; border-radius: 16px;
    padding: 1.25rem 1.4rem; margin-bottom: 1rem;
    box-shadow: 0 4px 15px rgba(25, 30, 60, 0.04); color: #172033; line-height: 1.6; }
.card-label { font-size: 0.72rem; font-weight: 700; color: #6f7590;
    text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.55rem; }
.card-date { font-weight: 700; margin-bottom: 0.3rem; }
.card-text { color: #4d5568; font-size: 0.95rem; }

.memory-card { background: linear-gradient(135deg, #5146c7 0%, #6c63df 100%);
    color: #ffffff; border-radius: 18px; padding: 1.5rem 1.6rem; margin-top: 1.4rem;
    box-shadow: 0 10px 28px rgba(81, 70, 199, 0.20); }
.memory-card-title { color: #dcd9ff; font-size: 0.72rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.6rem; }
.memory-card-text { color: #ffffff; font-size: 0.95rem; line-height: 1.6; }

.timeline-wrapper { margin-top: 1rem; margin-bottom: 0.5rem; }
.timeline-item { position: relative; border-left: 2px solid #d9d7fa;
    padding-left: 1.3rem; padding-bottom: 1.35rem; margin-left: 0.35rem; }
.timeline-item:last-child { border-left-color: transparent; padding-bottom: 0; }
.timeline-dot { position: absolute; width: 10px; height: 10px; background-color: #6257d8;
    border-radius: 50%; left: -6px; top: 4px; box-shadow: 0 0 0 4px #eeedff; }
.timeline-date { color: #858ba0; font-size: 0.78rem; font-weight: 600; }
.timeline-title { color: #172033; font-size: 0.98rem; font-weight: 700; margin-top: 0.18rem; }
.timeline-text { color: #737b8f; font-size: 0.88rem; margin-top: 0.2rem; line-height: 1.55; }

.stButton > button { width: 100%; border-radius: 11px; border: none;
    background: linear-gradient(135deg, #5146c7, #6c63df); color: white;
    font-weight: 700; padding: 0.72rem 1rem;
    box-shadow: 0 5px 14px rgba(81, 70, 199, 0.18); transition: all 0.2s ease; }
.stButton > button:hover { transform: translateY(-1px);
    box-shadow: 0 8px 18px rgba(81, 70, 199, 0.25); color: white; }

.stSelectbox label, .stTextArea label, .stDateInput label, .stTextInput label {
    color: #4d5568; font-weight: 600; }
textarea { border-radius: 12px !important; }
div[data-testid="stAlert"] { border-radius: 12px; }
hr { border-color: #e7e9f0; }

.badge-before { display: inline-block; background: #fff1f0; color: #c0392b;
    border: 1px solid #f5c6c2; padding: 0.35rem 0.8rem; border-radius: 999px;
    font-size: 0.8rem; font-weight: 700; margin-bottom: 0.7rem; }
.badge-after { display: inline-block; background: #eaf8ef; color: #1e8449;
    border: 1px solid #b7e4c7; padding: 0.35rem 0.8rem; border-radius: 999px;
    font-size: 0.8rem; font-weight: 700; margin-bottom: 0.7rem; }
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


# ============================================================
# HELPERS
# ============================================================

def esc(text) -> str:
    return html.escape(str(text))


def render(markup: str) -> None:
    st.markdown(markup, unsafe_allow_html=True)


def section_title(text: str) -> None:
    render(f'<div class="section-title">{esc(text)}</div>')


def card(label: str, body_html: str) -> None:
    render(
        f'<div class="brief-card">'
        f'<div class="card-label">{esc(label)}</div>'
        f'{body_html}'
        f'</div>'
    )


def to_promises(items):
    return [{"text": item, "done": False} for item in items]


def get_contacts():
    return sorted(load_memory().keys())


def get_contact_data(name):
    data = load_memory()
    key = find_contact(name, data)
    if key is None:
        return None
    return data[key]


def format_date(value):
    if not value:
        return "Unknown date"
    try:
        return date.fromisoformat(str(value)).strftime("%d %b ")
    except Exception:
        return str(value)


def show_ledger_items(items):
    if not items:
        st.caption("No commitments recorded.")
        return
    for item in items:
        deadline = item["deadline"].strftime("%d %b") if item.get("deadline") else "No deadline"
        if item["done"]:
            st.success(f'{item["text"]} · {deadline} · Completed')
        elif item.get("deadline") and item["deadline"] < date.today():
            st.error(f'{item["text"]} · {deadline} · Overdue')
        else:
            st.warning(f'{item["text"]} · {deadline} · Outstanding')


def brief_without_memory(name):
    prompt = f"""I have a meeting with {name} soon. Write a short meeting-prep brief with these
sections: Last meeting / Missed follow-ups / Still open / Talking points.
You have no records of any past interaction with {name}. Do not invent any
details. If you do not know something, say so plainly.

Format: use simple Markdown headings and bullet points only.
Do not use tables. Do not use HTML tags."""
    text = generate(prompt)
    return text.replace("<br>", "\n").replace("<br/>", "\n")


# ============================================================
# SIDEBAR
# ============================================================

contacts = get_contacts()

with st.sidebar:
    render('<div class="sidebar-brand">Meeting Prep</div>')
    render('<div class="sidebar-subtitle">Your relationship memory assistant</div>')
    render('<div class="sidebar-section">Navigation</div>')

    page = st.radio(
        "Navigation",
        ["Prepare for Meeting", "Before / After Memory", "Log Meeting"],
        label_visibility="collapsed",
    )

    st.divider()
    render('<div class="sidebar-section">Memory System</div>')

    if contacts:
        st.write(f"Hindsight memory active · {len(contacts)} contact(s) remembered.")
    else:
        st.write("Hindsight memory active · No meetings stored yet.")


# ============================================================
# HEADER
# ============================================================

header_col1, header_col2 = st.columns([5, 1])

with header_col1:
    render('<div class="app-title">Meeting Prep Agent</div>')
    render('<div class="app-subtitle">Your memory-powered meeting assistant</div>')

with header_col2:
    render('<div class="memory-status">Memory Active</div>')


# ============================================================
# PAGE 1: PREPARE FOR MEETING
# ============================================================

if page == "Prepare for Meeting":

    section_title("Prepare for your meeting")

    if not contacts:
        st.info("No meetings have been stored yet. Go to 'Log Meeting' and add your first meeting.")
        st.stop()

    selected_contact = st.selectbox("Who are you meeting?", contacts)

    contact = get_contact_data(selected_contact)
    if contact is None:
        st.error("Could not load this contact.")
        st.stop()

    meetings = contact.get("meetings", [])
    meetings_sorted = sorted(meetings, key=lambda m: str(m.get("date", "")), reverse=True)
    last_meeting = meetings_sorted[0] if meetings_sorted else None
    meeting_count = len(meetings)

    # Open / overdue counts from the same ledger the brief uses
    _, _, _ledger = build_ledger(selected_contact)
    open_items = [i for i in (_ledger or []) if not i["done"]]
    overdue_count = len([
        i for i in open_items
        if i["deadline"] and i["deadline"] < date.today()
    ])

    render(
        f'<div class="contact-card">'
        f'<div class="contact-name">{esc(selected_contact)}</div>'
        f'<div class="contact-details">{meeting_count} remembered meeting(s)</div>'
        f'</div>'
    )

    last_date = format_date(last_meeting.get("date")) if last_meeting else "No meetings"

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Meetings remembered", meeting_count)
    col2.metric("Open follow-ups", len(open_items))
    col3.metric("Overdue", overdue_count)
    col4.metric("Last meeting", last_date)

    st.write("")

    prepare = st.button("Prepare Meeting Brief")

    if prepare:
        with st.spinner("Recalling relationship memory and preparing your brief..."):
            try:
                st.session_state["brief"] = {
                    "contact": selected_contact,
                    "text": make_brief(selected_contact),
                    "memories": recall_contact(selected_contact),
                    "ledger": build_ledger(selected_contact),
                }
            except Exception as e:
                st.error("The meeting brief could not be generated.")
                st.exception(e)
                st.stop()

    saved = st.session_state.get("brief")

    if saved and saved["contact"] == selected_contact:

        brief_text = saved["text"]
        memories = saved["memories"]
        ledger_result = saved["ledger"]

        st.divider()
        section_title("Meeting Brief")

        with st.container(border=True):
            st.caption("AI-GENERATED BRIEF")
            st.markdown(brief_text)

        if last_meeting:
            card(
                "Last Conversation",
                f'<div class="card-date">{esc(format_date(last_meeting.get("date")))}</div>'
                f'<div class="card-text">{esc(last_meeting.get("summary", ""))}</div>',
            )

        if ledger_result and ledger_result[2] is not None:
            ledger_items = ledger_result[2]
            your_items = [i for i in ledger_items if i["side"] == "you_promised"]
            their_items = [i for i in ledger_items if i["side"] == "they_promised"]

            c1, c2 = st.columns(2)
            with c1:
                section_title("Your Commitments")
                show_ledger_items(your_items)
            with c2:
                section_title("Their Commitments")
                show_ledger_items(their_items)

        st.divider()
        section_title("What Hindsight Remembers")

        if memories:
            st.write(f"Hindsight recalled {len(memories)} memory items about {selected_contact}. Showing the top 6.")
            for memory in memories[:6]:
                card("Remembered Context", f'<div class="card-text">{esc(memory)}</div>')
        else:
            st.info("No additional Hindsight memories were returned for this contact.")

        section_title("Relationship Timeline")

        if meetings_sorted:
            items_html = ""
            for meeting in meetings_sorted:
                items_html += (
                    '<div class="timeline-item">'
                    '<div class="timeline-dot"></div>'
                    f'<div class="timeline-date">{esc(format_date(meeting.get("date")))}</div>'
                    '<div class="timeline-title">Meeting</div>'
                    f'<div class="timeline-text">{esc(meeting.get("summary", ""))}</div>'
                    '</div>'
                )
            render(f'<div class="timeline-wrapper">{items_html}</div>')

        render(
            '<div class="memory-card">'
            '<div class="memory-card-title">Persistent Relationship Memory</div>'
            '<div class="memory-card-text">'
            f'The assistant has remembered <strong>{esc(selected_contact)}</strong> '
            f'across {meeting_count} meeting(s).'
            '</div>'
            '<div class="memory-card-text" style="margin-top: 0.7rem;">'
            'Meeting history, commitments, completed follow-ups, relationship context, '
            'and your style preferences are recalled every time you prepare a meeting.'
            '</div>'
            '</div>'
        )

        st.divider()
        section_title("Teach the assistant")

        feedback = st.text_input(
            "How would you like future briefs to be written?",
            placeholder="Example: Keep the last-meeting summary to 2 lines and add a mood note.",
        )

        if st.button("Remember This Preference"):
            if not feedback.strip():
                st.warning("Please enter a preference first.")
            else:
                try:
                    retain_preference(feedback.strip())
                    st.success("Preference saved to Hindsight memory. Your next brief will follow it.")
                except Exception as e:
                    st.error("The preference could not be saved.")
                    st.exception(e)


# ============================================================
# PAGE 2: BEFORE / AFTER MEMORY
# ============================================================

elif page == "Before / After Memory":

    section_title("Same request. With and without memory.")

    st.write(
        "The same AI, the same request. The only difference is whether "
        "it has Hindsight memory of past meetings."
    )

    if not contacts:
        st.info("No contacts yet. Load demo data first.")
        st.stop()

    demo_contact = st.selectbox("Who are you meeting?", contacts, key="demo_contact")

    if st.button("Run comparison"):
        left, right = st.columns(2)

        with left:
            render('<div class="badge-before">WITHOUT MEMORY</div>')
            with st.spinner("Generating a brief with no memory..."):
                try:
                    plain = brief_without_memory(demo_contact)
                except Exception as e:
                    plain = f"Could not generate: {e}"
            with st.container(border=True):
                st.markdown(plain)

        with right:
            render('<div class="badge-after">WITH HINDSIGHT MEMORY</div>')
            with st.spinner("Recalling everything about " + demo_contact + "..."):
                try:
                    full = make_brief(demo_contact)
                except Exception as e:
                    full = f"Could not generate: {e}"
            with st.container(border=True):
                st.markdown(full)


# ============================================================
# PAGE 3: LOG MEETING
# ============================================================

elif page == "Log Meeting":

    section_title("Log a New Meeting")

    st.write(
        "Paste your raw meeting notes. The AI extracts the summary and commitments, "
        "then stores the meeting in the ledger and in Hindsight memory."
    )

    st.write("")

    existing_contacts = get_contacts()

    contact_mode = st.radio("Contact", ["Existing contact", "New contact"], horizontal=True)

    if contact_mode == "Existing contact":
        if not existing_contacts:
            st.info("No contacts exist yet. Choose 'New contact' to create the first one.")
            st.stop()
        contact_name = st.selectbox("Select contact", existing_contacts)
    else:
        contact_name = st.text_input("Contact name", placeholder="e.g. Rahul Sharma")

    meeting_date = st.date_input("Meeting date", value=date.today())

    notes = st.text_area(
        "Meeting notes",
        placeholder=(
            "Paste or type your actual meeting notes here...\n\n"
            "Example:\n"
            "Discussed the launch timeline. I promised to send the updated proposal by Friday. "
            "They said they would confirm the budget next week."
        ),
        height=250,
    )

    st.write("")

    if st.button("Save Meeting"):

        if not contact_name.strip():
            st.error("Please enter a contact name.")

        elif not notes.strip():
            st.error("Please enter meeting notes first.")

        else:
            with st.spinner("Reading notes and updating relationship memory..."):
                try:
                    result = extract_meeting(notes.strip())

                    summary = result.get("summary", "")
                    you_promised = result.get("you_promised", [])
                    they_promised = result.get("they_promised", [])

                    add_meeting(
                        contact_name.strip(),
                        {
                            "date": str(meeting_date),
                            "summary": summary,
                            "you_promised": to_promises(you_promised),
                            "they_promised": to_promises(they_promised),
                        },
                    )

                    hindsight_error = None
                    try:
                        retain_meeting(
                            contact_name.strip(),
                            str(meeting_date),
                            summary,
                            you_promised,
                            they_promised,
                        )
                    except Exception as e:
                        hindsight_error = str(e)

                except Exception as e:
                    st.error("The meeting could not be processed.")
                    st.exception(e)
                    st.stop()

            st.success(f"Meeting with {contact_name.strip()} was saved.")

            if hindsight_error:
                st.warning("The meeting was saved locally, but Hindsight could not be updated.")
            else:
                st.success("Hindsight memory was updated.")

            section_title("AI Extraction")
            card("Summary", f'<div class="card-text">{esc(summary)}</div>')

            c1, c2 = st.columns(2)
            with c1:
                section_title("Your Commitments")
                if you_promised:
                    for item in you_promised:
                        st.warning(item)
                else:
                    st.caption("No commitment detected.")
            with c2:
                section_title("Their Commitments")
                if they_promised:
                    for item in they_promised:
                        st.warning(item)
                else:
                    st.caption("No commitment detected.")

            st.info(
                "This meeting is now part of the relationship memory. "
                "Go to 'Prepare for Meeting' to generate a brief using the accumulated memory."
            )