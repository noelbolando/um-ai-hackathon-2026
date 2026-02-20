"""
app.py
------
Ross Advisor — Learning Goal Dashboard.

Layout:
  [Top bar: learning goal input]
  [Left: Preferences] [Center-Left: Courses] [Center-Right: Faculty] [Right: Chat]

Run with:
    streamlit run app.py
"""

import streamlit as st
from agent import search_courses
from faculty_agent import search_faculty
from llm import (
    extract_search_query,
    explain_course_match,
    explain_faculty_match,
    generate_goal_response,
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MLearn",
    page_icon="〽️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;600;700&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    background: #E8EBF0;
    color: #1a1a2e;
}
.stApp { background: #E8EBF0; }
#MainMenu, footer, header { visibility: hidden; }
section[data-testid="stSidebar"] { display: none; }

/* ── Navbar ── */
.navbar {
    background: #00274C;
    padding: 0 1.5rem;
    height: 64px;
    display: flex;
    align-items: center;
    gap: 1rem;
    box-shadow: 0 2px 12px rgba(0,39,76,0.4);
    margin-bottom: 0;
}
.navbar-logo {
    background: #FFCB05;
    color: #00274C;
    font-family: 'Crimson Pro', serif;
    font-size: 1.6rem;
    font-weight: 700;
    width: 44px;
    height: 44px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    letter-spacing: -1px;
}
.navbar-title {
    color: white;
    font-family: 'Crimson Pro', serif;
    font-size: 1.2rem;
    font-weight: 600;
    letter-spacing: 0.01em;
}
.navbar-sub {
    color: #A8BFDC;
    font-size: 0.82rem;
    margin-left: 0.25rem;
}

/* ── Goal bar ── */
.goal-bar {
    background: #00274C;
    padding: 0.85rem 1.5rem 1rem 1.5rem;
    border-bottom: 3px solid #FFCB05;
    margin-bottom: 0;
    width: 100%;
}
.goal-label {
    color: #FFCB05;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.4rem;
}


/* ── Message history bar ── */
.history-bar {
    background: #f0f2f6;
    border-bottom: 1px solid #dde1ea;
    padding: 0.6rem 1.5rem;
    margin-bottom: 1rem;
}
.history-entry {
    display: flex;
    gap: 0.75rem;
    align-items: flex-start;
    padding: 0.5rem 0;
    border-bottom: 1px solid #e4e7ed;
}
.history-entry:last-child { border-bottom: none; }
.history-role-user {
    font-size: 0.72rem;
    font-weight: 700;
    color: #00274C;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    white-space: nowrap;
    padding-top: 0.1rem;
    min-width: 52px;
}
.history-role-ai {
    font-size: 0.72rem;
    font-weight: 700;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    white-space: nowrap;
    padding-top: 0.1rem;
    min-width: 52px;
}
.history-text {
    font-size: 0.83rem;
    color: #333;
    line-height: 1.5;
}
/* ── Panel ── */
.panel {
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 12px rgba(0,39,76,0.08);
    overflow: hidden;
    height: 100%;
}
.panel-header {
    padding: 0.85rem 1.1rem;
    border-bottom: 1px solid #EEF0F4;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.panel-title {
    font-family: 'Crimson Pro', serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: #00274C;
}
.panel-count {
    font-size: 0.75rem;
    background: #F0F3F7;
    color: #666;
    padding: 0.15rem 0.6rem;
    border-radius: 20px;
    font-weight: 500;
}

/* ── Preferences panel ── */
.pref-header {
    background: #00274C;
    color: #FFCB05;
    font-family: 'Crimson Pro', serif;
    font-size: 1.05rem;
    font-weight: 700;
    padding: 0.85rem 1.1rem;
    letter-spacing: 0.02em;
}
.pref-body { padding: 0.9rem 1rem; }
.pref-label {
    font-size: 0.72rem;
    font-weight: 600;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 0.35rem;
    margin-top: 0.75rem;
    display: block;
}
.credit-display {
    background: #F5F7FA;
    border: 1.5px solid #D0D5DD;
    border-radius: 8px;
    padding: 0.45rem 0.8rem;
    font-size: 1rem;
    font-weight: 600;
    color: #00274C;
    text-align: center;
    margin-top: 0.3rem;
}

/* ── Course card ── */
.course-card {
    padding: 0.9rem 1.1rem;
    border-bottom: 1px solid #EEF0F4;
    animation: fadeIn 0.25s ease forwards;
    opacity: 0;
}
.course-card:hover { background: #FAFBFC; }
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: translateY(0); }
}
.course-title {
    font-family: 'Crimson Pro', serif;
    font-size: 1rem;
    font-weight: 700;
    color: #00274C;
    margin-bottom: 0.25rem;
    line-height: 1.3;
}
.instructor-tag {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    background: #00274C;
    color: white;
    border-radius: 5px;
    padding: 0.12rem 0.45rem;
    font-size: 0.74rem;
    font-weight: 500;
    margin-bottom: 0.35rem;
}
.why-text {
    font-size: 0.8rem;
    color: #444;
    margin-bottom: 0.35rem;
    display: flex;
    align-items: flex-start;
    gap: 0.3rem;
    line-height: 1.4;
}
.why-text::before {
    content: '✓';
    color: #00274C;
    font-weight: 700;
    flex-shrink: 0;
}
.card-meta {
    font-size: 0.76rem;
    color: #888;
    margin-bottom: 0.4rem;
}
.card-meta .sep { color: #CCC; margin: 0 0.3rem; }

/* ── Faculty card ── */
.faculty-card {
    padding: 0.9rem 1.1rem;
    border-bottom: 1px solid #EEF0F4;
    animation: fadeIn 0.25s ease forwards;
    opacity: 0;
}
.faculty-card:hover { background: #FAFBFC; }
.faculty-name {
    font-family: 'Crimson Pro', serif;
    font-size: 1rem;
    font-weight: 700;
    color: #00274C;
    margin-bottom: 0.15rem;
}
.faculty-title-text {
    font-size: 0.76rem;
    color: #777;
    margin-bottom: 0.4rem;
    line-height: 1.4;
}
.why-faculty {
    font-size: 0.8rem;
    color: #444;
    background: #F5F7FA;
    border-left: 3px solid #FFCB05;
    padding: 0.4rem 0.65rem;
    border-radius: 0 6px 6px 0;
    margin-bottom: 0.4rem;
    line-height: 1.4;
    font-style: italic;
}
.profile-link {
    font-size: 0.78rem;
    color: #00274C;
    font-weight: 600;
    text-decoration: none;
}
.profile-link:hover { text-decoration: underline; }

/* ── Empty state ── */
.empty-state {
    padding: 2.5rem 1.2rem;
    text-align: center;
    color: #BBB;
}
.empty-icon { font-size: 2rem; margin-bottom: 0.6rem; }
.empty-text {
    font-family: 'Crimson Pro', serif;
    font-size: 1rem;
    color: #999;
}

/* ── Chat panel ── */
.chat-header {
    background: #F5F7FA;
    padding: 0.85rem 1.1rem;
    border-bottom: 1px solid #EEF0F4;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.chat-header-title {
    font-family: 'Crimson Pro', serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: #00274C;
}
.chat-history {
    padding: 0.85rem 0.9rem;
    display: flex;
    flex-direction: column;
    gap: 0.65rem;
    max-height: 420px;
    overflow-y: auto;
}
.chat-msg-user { display: flex; gap: 0.5rem; align-items: flex-start; }
.chat-avatar {
    width: 28px; height: 28px; border-radius: 50%;
    background: #00274C; color: #FFCB05;
    font-weight: 700; font-size: 0.7rem;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}
.chat-bubble-user {
    background: #F0F3F7;
    border-radius: 4px 10px 10px 10px;
    padding: 0.5rem 0.75rem;
    font-size: 0.8rem;
    color: #1a1a2e;
    line-height: 1.45;
    flex: 1;
}
.chat-msg-agent { display: flex; flex-direction: row-reverse; gap: 0.5rem; align-items: flex-start; }
.chat-avatar-agent {
    width: 28px; height: 28px; border-radius: 50%;
    background: #FFCB05; color: #00274C;
    font-weight: 700; font-size: 0.65rem;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}
.chat-bubble-agent {
    background: #E8F0FB;
    border-radius: 10px 4px 10px 10px;
    padding: 0.5rem 0.75rem;
    font-size: 0.8rem;
    color: #1a1a2e;
    line-height: 1.5;
    flex: 1;
}
.chat-input-section {
    padding: 0.7rem 0.9rem;
    border-top: 1px solid #EEF0F4;
    background: #FAFBFC;
}
.chat-input-label {
    font-size: 0.68rem;
    font-weight: 600;
    color: #999;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 0.35rem;
}

/* ── Streamlit overrides ── */
div[data-testid="stTextInput"] > div > div > input {
    border-radius: 8px !important;
    border: 1.5px solid #D0D5DD !important;
    background: white !important;
    color: #1a1a2e !important;
    caret-color: #00274C !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 0.9rem !important;
}
div[data-testid="stTextInput"] > div > div > input::placeholder {
    color: #AAB0BC !important;
    opacity: 1 !important;
    font-style: italic;
}
div[data-testid="stTextInput"] > div > div > input:focus {
    border-color: #00274C !important;
    box-shadow: 0 0 0 3px rgba(0,39,76,0.1) !important;
}

/* Goal bar input — white text on dark bg */
.goal-bar div[data-testid="stTextInput"] > div > div > input {
    background: rgba(255,255,255,0.1) !important;
    border-color: rgba(255,255,255,0.3) !important;
    color: white !important;
    caret-color: #FFCB05 !important;
}
.goal-bar div[data-testid="stTextInput"] > div > div > input::placeholder {
    color: rgba(255,255,255,0.45) !important;
}

div[data-testid="stForm"] { border: none !important; padding: 0 !important; background: transparent !important; }

.stButton > button {
    background: #FFCB05 !important;
    color: #00274C !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-weight: 700 !important;
    padding: 0.55rem 1.1rem !important;
    font-size: 0.88rem !important;
    width: 100% !important;
}
.stButton > button:hover { background: #FFD740 !important; }

div[data-testid="stSlider"] > div { padding: 0 !important; }
div[data-testid="stSlider"] label { display: none !important; }
div[data-testid="stSelectbox"] > div > div { border-radius: 8px !important; border: 1.5px solid #D0D5DD !important; font-size: 0.85rem !important; }

/* Progress bar — black */
.stProgress > div > div > div > div {
    background: #000000 !important;
}
.stProgress > div > div > div {
    background: #E0E0E0 !important;
    border-radius: 0 !important;
}
.stProgress {
    position: sticky;
    top: 0;
    z-index: 999;
    margin: 0 !important;
    padding: 0 !important;
}
div[data-testid="stStatusWidget"] { display: none; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #D0D5DD; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
defaults = {
    "messages": [],
    "courses": [],
    "faculty": [],
    "time_pref": "Morning",
    "credit_target": 12,
    "top_k": 10,
    "pending_query": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── NAVBAR ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="navbar">
    <div class="navbar-logo">M</div>
    <span class="navbar-title">MLearn</span>
</div>
""", unsafe_allow_html=True)

# ── GOAL BAR ──────────────────────────────────────────────────────────────────
st.markdown('<div class="goal-bar">', unsafe_allow_html=True)
st.markdown('<div class="goal-label" style="font-size:1.15rem; letter-spacing:0.01em; text-transform:none; font-family: Crimson Pro, serif; font-weight:600; color:#000000;">What do you want to learn or achieve?</div>', unsafe_allow_html=True)

with st.form("goal_form", clear_on_submit=True):
    goal_cols = st.columns([8, 1])
    with goal_cols[0]:
        goal_input = st.text_input(
            "goal",
            placeholder="e.g. I want to break into consulting, or I want to understand behavioral economics...",
            label_visibility="collapsed",
        )
    with goal_cols[1]:
        go = st.form_submit_button("Find →", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# ── MESSAGE HISTORY ──────────────────────────────────────────────────────────
if st.session_state.messages:
    st.markdown('<div class="history-bar">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        role_class = "history-role-user" if msg["role"] == "user" else "history-role-ai"
        role_label = "You" if msg["role"] == "user" else "MLearn"
        text = msg["content"]
        # Truncate long AI responses in the history view
        if msg["role"] == "assistant" and len(text) > 300:
            text = text[:300] + "..."
        st.markdown(
            f'<div class="history-entry">' +
            f'<span class="{role_class}">{role_label}</span>' +
            f'<span class="history-text">{text}</span>' +
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

# ── MAIN LAYOUT ───────────────────────────────────────────────────────────────
courses_col, faculty_col = st.columns([1, 1], gap="medium")

# ═══════════════════════════════
# CENTER-LEFT — Courses
# ═══════════════════════════════
with courses_col:
    courses = st.session_state.courses
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    course_count_html = f'<span class="panel-count">{len(courses)} found</span>' if courses else ""
    st.markdown(
        f'<div class="panel-header">'
        f'<span class="panel-title">📚 Recommended Courses</span>'
        f'{course_count_html}'
        f'</div>',
        unsafe_allow_html=True,
    )

    if not courses:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">📖</div>
            <div class="empty-text">Enter a learning goal to see course recommendations</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for i, c in enumerate(courses):
            delay = i * 0.06
            instructor = c.get("taught by", "")
            semester = c.get("semester taught", "")
            credits_val = c.get("credits", "")
            meeting = c.get("meeting times", "")
            prereqs = c.get("prerequisites", "")
            why = c.get("explanation", "")
            code = c.get("course code", "")
            desc = c.get("course description", "")
            short_desc = desc[:55] + ("..." if len(desc) > 55 else "")

            meta_parts = []
            if credits_val:
                meta_parts.append(f"{credits_val} cr")
            if meeting:
                meta_parts.append(meeting)
            if semester:
                meta_parts.append(semester)
            meta_str = "  ·  ".join(meta_parts)

            instructor_html = f'<div><span class="instructor-tag">👤 {instructor}</span></div>' if instructor else ""
            why_html = f'<div class="why-text">{why}</div>' if why else ""
            meta_html = f'<div class="card-meta">{meta_str}</div>' if meta_str else ""
            prereq_html = f'<div class="card-meta" style="font-size:0.73rem;">📋 {prereqs}</div>' if prereqs else ""

            st.markdown(f"""
            <div class="course-card" style="animation-delay:{delay}s">
                <div class="course-title">{code}: {short_desc}</div>
                {instructor_html}{why_html}{meta_html}{prereq_html}
            </div>
            """, unsafe_allow_html=True)



    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════
# CENTER-RIGHT — Faculty
# ═══════════════════════════════
with faculty_col:
    faculty = st.session_state.faculty
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    faculty_count_html = f'<span class="panel-count">{len(faculty)} found</span>' if faculty else ""
    st.markdown(
        f'<div class="panel-header">'
        f'<span class="panel-title">👤 Faculty to Connect With</span>'
        f'{faculty_count_html}'
        f'</div>',
        unsafe_allow_html=True,
    )

    if not faculty:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">🤝</div>
            <div class="empty-text">Enter a learning goal to find faculty to network with</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for i, f in enumerate(faculty):
            delay = i * 0.06
            why = f.get("explanation", "")
            profile = f.get("profile_url", "")

            why_html = f'<div class="why-faculty">{why}</div>' if why else ""
            profile_html = f'<a class="profile-link" href="{profile}" target="_blank">View Profile →</a>' if profile else ""

            st.markdown(f"""
            <div class="faculty-card" style="animation-delay:{delay}s">
                <div class="faculty-name">{f.get('name','')}</div>
                <div class="faculty-title-text">{f.get('titles','')}</div>
                {why_html}{profile_html}
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ── Trigger from goal bar ─────────────────────────────────────────────────────
if go and goal_input.strip():
    st.session_state.pending_query = goal_input.strip()
    st.rerun()

# ── Process query ─────────────────────────────────────────────────────────────
if st.session_state.pending_query:
    query = st.session_state.pending_query
    st.session_state.pending_query = None

    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
    st.session_state.messages.append({"role": "user", "content": query})

    progress = st.progress(0)
    try:
        progress.progress(15)
        search_query = extract_search_query(query, history)
        progress.progress(35)
        courses = search_courses(search_query, top_k=10)
        progress.progress(55)
        faculty = search_faculty(search_query, top_k=10)
        progress.progress(70)
        for c in courses:
            c["explanation"] = explain_course_match(c, query, history)
        progress.progress(85)
        for f in faculty:
            f["explanation"] = explain_faculty_match(f, query, history)
        progress.progress(95)
        response = generate_goal_response(query, courses, faculty, history)
        progress.progress(100)
        progress.empty()
        st.session_state.courses = courses
        st.session_state.faculty = faculty
        st.session_state.messages.append({"role": "assistant", "content": response})
    except Exception as e:
        progress.empty()
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"⚠️ Error: {str(e)}\n\nMake sure Ollama is running and both ingest scripts have been run."
        })
        st.session_state.courses = []
        st.session_state.faculty = []

    st.rerun()
