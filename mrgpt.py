import streamlit as st
import requests
import random
import time
import uuid
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

JSONBIN_API_KEY = os.getenv("JSONBIN_API_KEY", "")
JSONBIN_BIN_ID  = os.getenv("JSONBIN_BIN_ID", "")
ADMIN_KEY       = os.getenv("ADMIN_KEY", "admin123")
JSONBIN_URL     = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}"
HEADERS         = {"X-Master-Key": JSONBIN_API_KEY, "Content-Type": "application/json"}
MAX_QUESTIONS   = 5

WAITING_MESSAGES = [
    ("MrGPT is playing Minecraft right now.", "He'll answer you between rounds."),
    ("MrGPT is asleep.", "His dedication to your question is truly inspiring."),
    ("MrGPT is eating.", "Do not disturb. Seriously."),
    ("MrGPT has seen your message.", "He left it on read. Intentionally."),
    ("MrGPT stepped outside for some air.", "In January. Without a jacket."),
    ("MrGPT is watching YouTube.", '"For research purposes."'),
    ("MrGPT is arguing with someone online.", "Your question is next. Probably."),
    ("MrGPT is in the bathroom.", "This could take anywhere from 2 to 45 minutes."),
    ("MrGPT is making a playlist.", "Very relevant to your question, trust."),
    ("Consulting the ancient texts.", "(It's Reddit.)"),
    ("MrGPT battery: 2%.", "Peak performance mode activated."),
    ("MrGPT is mentally on vacation.", "Physically at his desk. Spiritually? Gone."),
    ("BEEP BOOP PROCESSING.", "This is definitely a real AI and not a person."),
    ("You are #1 in queue.*", "*Queue currently has 847 other questions."),
    ("MrGPT has entered sleep mode.", "Expected wake time: unknown."),
    ("MrGPT is thinking really hard.", "Or he forgot. Hard to tell."),
    ("Running at 12% capacity.", "This IS peak performance."),
    ("MrGPT rolled a die to decide if he'd answer.", "He got a 3. Whatever that means."),
    ("Neural pathways activating...", "Nothing is happening. We're working on it."),
    ("Transmitting across the servers.", "The servers are a guy named Dave."),
    ("MrGPT is getting coffee.", "Fourth cup today. He's fine."),
    ("Answers at the speed of thought.*", "*MrGPT's thoughts move quite slowly."),
    ("Cross-referencing 47 billion data points.", "The data points are vibes."),
    ("MrGPT is pondering your question.", "He finds it deeply confusing."),
    ("Loading...", "Has been loading since 2019."),
    ("MrGPT is feeding ducks.", "This is relevant to your query somehow."),
    ("Processing power at historic lows.", "Please hold."),
    ("MrGPT is in his feelings right now.", "Your question hit different."),
    ("MrGPT is at the gym.", "He will not be taking questions at this time."),
    ("Quantum inference in progress.", "The quantum is not cooperating."),
]

FAKE_STEPS = [
    "Tokenizing input vectors...",
    "Loading 847 billion parameters...",
    "Activating attention mechanism...",
    "Consulting the algorithm council...",
    "Running semantic analysis engine v4.2...",
    "Cross-referencing knowledge base...",
    "Performing quantum inference...",
    "Optimizing response coherence...",
    "97% complete...",
    "97% complete...",
    "97% complete...",
    "Still 97%... this is normal...",
    "97% complete (we promise)...",
]

ANIM_MODES = ["nasa", "chaos", "cinematic"]

def get_data():
    try:
        r = requests.get(f"{JSONBIN_URL}/latest", headers=HEADERS, timeout=8)
        return r.json().get("record", {"questions": []})
    except:
        return {"questions": []}

def save_data(data):
    try:
        requests.put(JSONBIN_URL, headers=HEADERS, json=data, timeout=8)
    except:
        pass

def submit_question(question_text):
    data = get_data()
    qid = str(uuid.uuid4())[:8].upper()
    data["questions"].append({
        "id": qid,
        "question": question_text,
        "answer": None,
        "status": "pending",
        "asked_at": datetime.now().isoformat(),
        "answered_at": None,
    })
    if len(data["questions"]) > MAX_QUESTIONS:
        data["questions"] = data["questions"][-MAX_QUESTIONS:]
    save_data(data)
    return qid

def get_question(qid):
    data = get_data()
    for q in data["questions"]:
        if q["id"].upper() == qid.upper():
            return q
    return None

def answer_question(qid, answer_text):
    data = get_data()
    for q in data["questions"]:
        if q["id"].upper() == qid.upper():
            q["answer"] = answer_text
            q["status"] = "answered"
            q["answered_at"] = datetime.now().isoformat()
            break
    save_data(data)

def delete_question(qid):
    data = get_data()
    data["questions"] = [q for q in data["questions"] if q["id"].upper() != qid.upper()]
    save_data(data)

st.set_page_config(page_title="MrGPT", page_icon="🤖", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    background-color: #141414;
    color: #e8e8e8;
    font-family: 'Space Grotesk', ui-sans-serif, system-ui, sans-serif;
}

.block-container {
    max-width: 780px !important;
    padding: 0 2rem !important;
    margin: 0 auto;
}

/* Show sidebar toggle arrow always */
[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    background: #1e1e1e !important;
    border-right: 1px solid #2a2a2a !important;
}
[data-testid="collapsedControl"] svg { fill: #888 !important; }

#MainMenu, footer, header { visibility: hidden; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #0f0f0f !important;
    border-right: 1px solid #242424;
}
[data-testid="stSidebar"] .block-container {
    padding: 1.2rem 0.9rem !important;
    max-width: 100% !important;
}
[data-testid="stSidebarContent"] { padding: 0 !important; }

[data-testid="stSidebar"] .stButton > button {
    background: transparent;
    color: #888;
    border: none;
    border-radius: 8px;
    font-size: 0.85em;
    font-weight: 400;
    padding: 0.5rem 0.75rem;
    text-align: left;
    width: 100%;
    transition: all 0.12s;
    font-family: 'Space Grotesk', sans-serif;
    letter-spacing: 0.01em;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #1e1e1e;
    color: #e8e8e8;
}

/* Main buttons */
section.main .stButton > button {
    background: #1e1e1e;
    color: #e8e8e8;
    border: 1px solid #333;
    border-radius: 10px;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 500;
    font-size: 0.92em;
    letter-spacing: 0.02em;
    padding: 0.65em 1.3em;
    transition: all 0.15s;
    width: 100%;
}
section.main .stButton > button:hover {
    background: #282828;
    border-color: #484848;
    transform: translateY(-1px);
}

/* Textarea */
.stTextArea textarea {
    background: #1e1e1e;
    border: 1.5px solid #2e2e2e;
    border-radius: 18px;
    color: #e8e8e8;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1em;
    line-height: 1.65;
    padding: 1.1rem 1.3rem;
    resize: none;
    transition: border-color 0.15s, box-shadow 0.15s;
}
.stTextArea textarea:focus {
    border-color: #ff5722;
    box-shadow: 0 0 0 3px rgba(255,87,34,0.1);
    outline: none;
}
.stTextArea textarea::placeholder { color: #444; }

/* Text input */
.stTextInput input {
    background: #1e1e1e !important;
    border: 1.5px solid #2e2e2e !important;
    border-radius: 10px !important;
    color: #e8e8e8 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    letter-spacing: 0.02em !important;
}
.stTextInput input:focus {
    border-color: #ff5722 !important;
    box-shadow: 0 0 0 3px rgba(255,87,34,0.1) !important;
}
.stTextInput input::placeholder { color: #444 !important; }

[data-testid="stContainer"] {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 14px;
}

[data-testid="stExpander"] {
    background: #161616;
    border: 1px solid #252525;
    border-radius: 10px;
}

hr { border-color: #222 !important; }

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #0f0f0f; }
::-webkit-scrollbar-thumb { background: #2e2e2e; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #3e3e3e; }

/* ── ANIMATIONS ── */
@keyframes fadein {
    from { opacity: 0; transform: translateY(14px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes blink {
    0%,100% { opacity: 1; } 50% { opacity: 0; }
}
@keyframes pulse-dot {
    0%,100% { opacity: 0.3; transform: scale(0.7); }
    50% { opacity: 1; transform: scale(1); }
}

/* NASA shapes */
@keyframes orbit-1 {
    from { transform: rotate(0deg) translateX(90px) rotate(0deg); }
    to   { transform: rotate(360deg) translateX(90px) rotate(-360deg); }
}
@keyframes orbit-2 {
    from { transform: rotate(120deg) translateX(60px) rotate(-120deg); }
    to   { transform: rotate(480deg) translateX(60px) rotate(-480deg); }
}
@keyframes orbit-3 {
    from { transform: rotate(240deg) translateX(75px) rotate(-240deg); }
    to   { transform: rotate(600deg) translateX(75px) rotate(-600deg); }
}
@keyframes spin-ring {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
}
@keyframes spin-ring-rev {
    from { transform: rotate(0deg); }
    to   { transform: rotate(-360deg); }
}
@keyframes nasa-pulse {
    0%,100% { box-shadow: 0 0 0 0 rgba(255,87,34,0.4); }
    50% { box-shadow: 0 0 0 20px rgba(255,87,34,0); }
}
@keyframes nasa-bar {
    0% { width: 0%; }
    20% { width: 23%; } 40% { width: 47%; }
    60% { width: 79%; } 80% { width: 93%; }
    90% { width: 97%; } 100% { width: 97%; }
}

/* CHAOS shapes */
@keyframes chaos-spin {
    from { transform: rotate(0deg) scale(1); }
    25% { transform: rotate(97deg) scale(1.3); }
    50% { transform: rotate(180deg) scale(0.7); }
    75% { transform: rotate(263deg) scale(1.2); }
    to   { transform: rotate(360deg) scale(1); }
}
@keyframes chaos-fly-1 {
    0%   { transform: translate(0,0) rotate(0deg); }
    20%  { transform: translate(40px,-30px) rotate(72deg); }
    40%  { transform: translate(-20px,50px) rotate(144deg); }
    60%  { transform: translate(60px,20px) rotate(216deg); }
    80%  { transform: translate(-40px,-40px) rotate(288deg); }
    100% { transform: translate(0,0) rotate(360deg); }
}
@keyframes chaos-fly-2 {
    0%   { transform: translate(0,0) rotate(0deg) scale(1); }
    33%  { transform: translate(-50px,30px) rotate(120deg) scale(1.5); }
    66%  { transform: translate(30px,-50px) rotate(240deg) scale(0.6); }
    100% { transform: translate(0,0) rotate(360deg) scale(1); }
}
@keyframes chaos-fly-3 {
    0%   { transform: translate(0,0) rotate(45deg); }
    25%  { transform: translate(30px,40px) rotate(135deg); }
    50%  { transform: translate(-40px,20px) rotate(225deg); }
    75%  { transform: translate(20px,-30px) rotate(315deg); }
    100% { transform: translate(0,0) rotate(405deg); }
}
@keyframes glitch-text {
    0%,100% { transform: translate(0); filter: none; color: #e8e8e8; }
    8%  { transform: translate(-3px,1px); filter: hue-rotate(90deg); color: #ff5722; }
    16% { transform: translate(3px,-1px); filter: hue-rotate(180deg); color: #ffaa00; }
    24% { transform: translate(0); filter: none; color: #e8e8e8; }
    50% { transform: translate(2px,2px); filter: brightness(1.4); }
    58% { transform: translate(-2px,-2px); filter: none; }
}
@keyframes flicker {
    0%,100% { opacity: 1; } 4% { opacity: 0.2; }
    8% { opacity: 1; } 52% { opacity: 1; }
    55% { opacity: 0.3; } 58% { opacity: 1; }
}

/* CINEMATIC shapes */
@keyframes cin-float-1 {
    0%,100% { transform: translateY(0) rotate(0deg); filter: drop-shadow(0 0 15px rgba(255,87,34,0.5)); }
    50%      { transform: translateY(-25px) rotate(180deg); filter: drop-shadow(0 0 35px rgba(255,87,34,0.9)); }
}
@keyframes cin-float-2 {
    0%,100% { transform: translateY(0) rotate(45deg) scale(1); }
    50%      { transform: translateY(-18px) rotate(225deg) scale(1.15); }
}
@keyndef cin-float-3 {
    0%,100% { transform: translateX(0) rotate(0deg); opacity: 0.6; }
    50%      { transform: translateX(12px) rotate(180deg); opacity: 1; }
}
@keyframes cin-reveal {
    0% { opacity: 0; transform: scaleX(0); }
    100% { opacity: 1; transform: scaleX(1); }
}
@keyframes cin-glow {
    0%,100% { filter: drop-shadow(0 0 8px rgba(255,87,34,0.3)); }
    50% { filter: drop-shadow(0 0 25px rgba(255,87,34,0.8)) drop-shadow(0 0 50px rgba(255,140,0,0.4)); }
}
@keyframes slow-pulse {
    0%,100% { opacity: 0.5; } 50% { opacity: 1; }
}
@keyframes progress-stuck {
    0% { width: 0%; } 60% { width: 97%; } 100% { width: 97%; }
}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
defaults = {
    "page": "home", "question_id": None, "question_text": "",
    "answer": None, "msg_index": 0, "step_index": 0,
    "anim_mode": "cinematic", "show_admin_input": False,
    "chat_history": [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

params = st.query_params
is_admin = params.get("admin", "") == ADMIN_KEY

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:0.4rem 0.2rem 1.2rem;'>
        <div style='display:flex;align-items:center;gap:0.6rem;margin-bottom:0.8rem;'>
            <div style='width:30px;height:30px;background:linear-gradient(135deg,#ff5722,#e64a19);
                border-radius:8px;display:flex;align-items:center;justify-content:center;
                font-size:0.9rem;flex-shrink:0;box-shadow:0 4px 12px rgba(255,87,34,0.3);'>🤖</div>
            <span style='font-weight:700;font-size:1.05em;color:#e8e8e8;font-family:Space Grotesk,sans-serif;letter-spacing:-0.01em;'>MrGPT</span>
        </div>
        <div style='background:#1a1a1a;border:1px solid #2a2a2a;border-radius:8px;
            padding:0.35rem 0.7rem;font-size:0.7em;color:#555;
            display:flex;justify-content:space-between;align-items:center;
            font-family:Space Mono,monospace;'>
            <span>MrGPT-9 Turbo Ultra Pro Max</span><span style='color:#333;'>▾</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("✏️  New chat", key="sb_new", use_container_width=True):
        st.session_state.page = "home"
        st.session_state.question_id = None
        st.session_state.question_text = ""
        st.session_state.answer = None
        st.rerun()

    if st.button("ℹ️  About MrGPT", key="sb_about", use_container_width=True):
        st.session_state.page = "about"
        st.rerun()

    st.markdown("<hr style='border-color:#1e1e1e;margin:0.5rem 0;'>", unsafe_allow_html=True)

    if st.session_state.chat_history:
        st.markdown("<div style='font-size:0.65em;color:#3a3a3a;padding:0 0.4rem 0.5rem;text-transform:uppercase;letter-spacing:0.08em;font-family:Space Mono,monospace;'>Recent</div>", unsafe_allow_html=True)
        for i, chat in enumerate(reversed(st.session_state.chat_history[-8:])):
            label = chat["question"][:30] + ("…" if len(chat["question"]) > 30 else "")
            if st.button(f"💬  {label}", key=f"hist_{i}", use_container_width=True):
                st.session_state.question_text = chat["question"]
                st.session_state.answer = chat["answer"]
                st.session_state.page = "answered"
                st.rerun()
    else:
        st.markdown("<div style='font-size:0.75em;color:#2a2a2a;padding:0.5rem;text-align:center;font-family:Space Mono,monospace;'>No chats yet</div>", unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#1e1e1e;margin:0.5rem 0;'>", unsafe_allow_html=True)

    if st.button("⚙️", key="sb_admin_toggle", use_container_width=True):
        st.session_state.show_admin_input = not st.session_state.show_admin_input
        st.rerun()

    if st.session_state.show_admin_input:
        pw = st.text_input("", type="password", placeholder="Access code",
                           label_visibility="collapsed", key="sb_admin_pw")
        if pw == ADMIN_KEY:
            st.session_state.page = "admin_verified"
            st.session_state.show_admin_input = False
            st.rerun()
        elif pw:
            st.markdown("<div style='font-size:0.72em;color:#e05;padding:0.2rem 0.5rem;'>Incorrect.</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ADMIN
# ══════════════════════════════════════════════════════════════════════════════
if is_admin or st.session_state.page == "admin_verified":
    col_back, col_title, col_refresh = st.columns([1, 4, 1])
    with col_back:
        st.markdown("<div style='padding-top:0.5rem;'></div>", unsafe_allow_html=True)
        if st.button("← Back", key="admin_back"):
            st.session_state.page = "home"
            st.rerun()
    with col_title:
        st.markdown("""
        <div style='padding:0.4rem 0 1.5rem;'>
            <div style='font-size:0.7em;color:#444;margin-bottom:0.2rem;font-family:Space Mono,monospace;letter-spacing:0.08em;'>STAFF · MrGPT</div>
            <div style='font-size:1.5em;font-weight:700;color:#e8e8e8;letter-spacing:-0.02em;'>Inbox</div>
        </div>
        """, unsafe_allow_html=True)
    with col_refresh:
        st.markdown("<div style='padding-top:0.5rem;'></div>", unsafe_allow_html=True)
        if st.button("↻ Refresh", key="admin_refresh"):
            st.rerun()

    data = get_data()
    pending = [q for q in data["questions"] if q["status"] == "pending"]
    answered = [q for q in data["questions"] if q["status"] == "answered"]

    if not pending:
        st.markdown("""
        <div style='text-align:center;padding:5rem 0;color:#3a3a3a;'>
            <div style='font-size:2.5rem;margin-bottom:0.8rem;'>✓</div>
            <div style='font-size:0.95em;font-family:Space Grotesk,sans-serif;'>All caught up. Go touch grass.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='color:#ff5722;font-size:0.78em;font-weight:600;margin-bottom:1.2rem;letter-spacing:0.08em;font-family:Space Mono,monospace;'>{len(pending)} PENDING</div>", unsafe_allow_html=True)
        for q in pending:
            with st.container(border=True):
                asked_time = q["asked_at"][:16].replace("T", " at ")
                st.markdown(f"""
                <div style='font-size:0.65em;color:#444;margin-bottom:0.5rem;font-family:Space Mono,monospace;'>{asked_time} · #{q['id']}</div>
                <div style='font-size:1.05em;color:#e8e8e8;margin-bottom:1rem;line-height:1.5;font-weight:500;font-family:Space Grotesk,sans-serif;'>"{q['question']}"</div>
                """, unsafe_allow_html=True)
                answer = st.text_area("", key=f"ans_{q['id']}", height=80,
                                      placeholder="Reply as MrGPT...", label_visibility="collapsed")
                c1, c2 = st.columns([5, 1])
                with c1:
                    if st.button("Send reply", key=f"sub_{q['id']}", use_container_width=True):
                        if answer.strip():
                            answer_question(q["id"], answer.strip())
                            st.success("Sent.")
                            time.sleep(0.5)
                            st.rerun()
                with c2:
                    if st.button("✕", key=f"del_{q['id']}", use_container_width=True):
                        delete_question(q["id"])
                        st.rerun()

    if answered:
        st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)
        with st.expander(f"History — {len(answered)} answered"):
            for q in reversed(answered):
                st.markdown(f"""
                <div style='margin-bottom:1rem;padding:0.9rem;background:#111;border-radius:8px;'>
                    <div style='color:#444;font-size:0.8em;margin-bottom:0.4rem;font-family:Space Grotesk,sans-serif;'>Q: {q['question']}</div>
                    <div style='color:#e8e8e8;font-size:0.88em;line-height:1.55;font-family:Space Grotesk,sans-serif;'>A: {q['answer']}</div>
                </div>
                """, unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# ABOUT
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "about":
    st.markdown("""
    <div style='text-align:center;padding:3.5rem 0 2rem;animation:fadein 0.4s ease;'>
        <h1 style='font-size:2.2rem;font-weight:700;color:#e8e8e8;margin-bottom:0.3rem;letter-spacing:-0.03em;'>About MrGPT</h1>
        <p style='color:#444;font-size:0.88em;font-family:Space Mono,monospace;'>The world's most advanced AI.*</p>
        <p style='color:#222;font-size:0.62em;font-family:Space Mono,monospace;'>*claims not independently verified</p>
    </div>
    <div style='display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:2rem;'>
        <div style='background:#1a1a1a;border:1px solid #2a2a2a;border-radius:14px;padding:1.3rem;text-align:center;'>
            <div style='font-size:2.2rem;font-weight:800;color:#ff5722;font-family:Space Grotesk,sans-serif;'>1,847,293</div>
            <div style='font-size:0.75em;color:#555;margin-top:0.2rem;'>Questions Answered</div>
            <div style='font-size:0.58em;color:#222;font-family:Space Mono,monospace;'>*number completely made up</div>
        </div>
        <div style='background:#1a1a1a;border:1px solid #2a2a2a;border-radius:14px;padding:1.3rem;text-align:center;'>
            <div style='font-size:2.2rem;font-weight:800;color:#ff5722;font-family:Space Grotesk,sans-serif;'>99.7%</div>
            <div style='font-size:0.75em;color:#555;margin-top:0.2rem;'>Accuracy Rate</div>
            <div style='font-size:0.58em;color:#222;font-family:Space Mono,monospace;'>*not measured</div>
        </div>
        <div style='background:#1a1a1a;border:1px solid #2a2a2a;border-radius:14px;padding:1.3rem;text-align:center;'>
            <div style='font-size:2.2rem;font-weight:800;color:#ff5722;font-family:Space Grotesk,sans-serif;'>GPT-9</div>
            <div style='font-size:0.75em;color:#555;margin-top:0.2rem;'>Model Version</div>
            <div style='font-size:0.58em;color:#222;font-family:Space Mono,monospace;'>*ahead of OpenAI by several years</div>
        </div>
        <div style='background:#1a1a1a;border:1px solid #2a2a2a;border-radius:14px;padding:1.3rem;text-align:center;'>
            <div style='font-size:2.2rem;font-weight:800;color:#ff5722;font-family:Space Grotesk,sans-serif;'>&lt;∞ms</div>
            <div style='font-size:0.75em;color:#555;margin-top:0.2rem;'>Response Time</div>
            <div style='font-size:0.58em;color:#222;font-family:Space Mono,monospace;'>*technically true</div>
        </div>
    </div>
    <div style='background:#1a1a1a;border:1px solid #2a2a2a;border-radius:14px;padding:1.5rem;margin-bottom:1.5rem;'>
        <div style='font-size:0.72em;font-weight:600;color:#ff5722;margin-bottom:0.8rem;text-transform:uppercase;letter-spacing:0.08em;font-family:Space Mono,monospace;'>About Our Technology</div>
        <p style='color:#999;font-size:0.9em;line-height:1.75;font-family:Space Grotesk,sans-serif;'>MrGPT is powered by our proprietary Neural Cognition Engine™, trained on over 47 billion data points gathered from across the internet, several encyclopedias, and at least one fortune cookie.</p>
        <p style='color:#999;font-size:0.9em;line-height:1.75;margin-top:0.8rem;font-family:Space Grotesk,sans-serif;'>Our model achieves state-of-the-art results on all benchmarks we chose to include. Benchmarks that did not produce favorable results were excluded for scientific reasons.</p>
        <p style='color:#333;font-size:0.68em;margin-top:1rem;font-family:Space Mono,monospace;'>MrGPT Industries LLC is not responsible for any advice given, consequences thereof, or feelings of confusion.</p>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HOME
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "home":
    st.markdown("""
    <div style='text-align:center;padding:5rem 0 2.5rem;animation:fadein 0.4s ease;'>
        <div style='
            width:58px;height:58px;
            background:linear-gradient(135deg,#ff5722,#e64a19);
            border-radius:15px;
            display:inline-flex;align-items:center;justify-content:center;
            font-size:1.8rem;margin-bottom:1.3rem;
            box-shadow:0 8px 32px rgba(255,87,34,0.35);
        '>🤖</div>
        <h1 style='font-size:2.2rem;font-weight:700;color:#e8e8e8;margin:0 0 0.5rem;letter-spacing:-0.03em;font-family:Space Grotesk,sans-serif;'>
            What can I help with?
        </h1>
        <p style='color:#444;font-size:0.85em;margin:0;font-family:Space Mono,monospace;'>Powered by MrGPT™ Neural Engine v9.4</p>
    </div>
    """, unsafe_allow_html=True)

    question = st.text_area("", placeholder="Message MrGPT...",
                             height=110, label_visibility="collapsed")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("↑  Send message", use_container_width=True):
            if question.strip():
                qid = submit_question(question.strip())
                st.session_state.question_id = qid
                st.session_state.question_text = question.strip()
                st.session_state.page = "waiting"
                st.session_state.msg_index = random.randint(0, len(WAITING_MESSAGES)-1)
                st.session_state.step_index = 0
                st.session_state.anim_mode = random.choice(ANIM_MODES)
                st.rerun()
            else:
                st.warning("Type something first.")

    st.markdown("""
    <div style='display:flex;flex-wrap:wrap;gap:0.5rem;justify-content:center;margin-top:1.5rem;'>
        <div style='background:#1a1a1a;border:1px solid #2a2a2a;border-radius:20px;padding:0.4rem 1rem;font-size:0.8em;color:#888;font-family:Space Grotesk,sans-serif;'>✨ Explain something</div>
        <div style='background:#1a1a1a;border:1px solid #2a2a2a;border-radius:20px;padding:0.4rem 1rem;font-size:0.8em;color:#888;font-family:Space Grotesk,sans-serif;'>💡 Give me ideas</div>
        <div style='background:#1a1a1a;border:1px solid #2a2a2a;border-radius:20px;padding:0.4rem 1rem;font-size:0.8em;color:#888;font-family:Space Grotesk,sans-serif;'>🤔 Ask anything</div>
        <div style='background:#1a1a1a;border:1px solid #2a2a2a;border-radius:20px;padding:0.4rem 1rem;font-size:0.8em;color:#888;font-family:Space Grotesk,sans-serif;'>🎯 Help me decide</div>
    </div>
    <div style='text-align:center;margin-top:4rem;color:#222;font-size:0.7em;font-family:Space Mono,monospace;'>
        MrGPT can make mistakes. Consider checking important info.
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# WAITING
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "waiting":
    q_text = st.session_state.question_text
    headline, subline = WAITING_MESSAGES[st.session_state.msg_index % len(WAITING_MESSAGES)]
    step = FAKE_STEPS[st.session_state.step_index % len(FAKE_STEPS)]
    mode = st.session_state.anim_mode

    # User bubble
    st.markdown(f"""
    <div style='display:flex;justify-content:flex-end;margin:2.5rem 0 1.5rem;animation:fadein 0.3s ease;'>
        <div style='background:#1e1e1e;border:1px solid #2e2e2e;border-radius:18px 18px 4px 18px;
            padding:0.9rem 1.2rem;max-width:78%;color:#e8e8e8;font-size:0.95em;line-height:1.65;
            font-family:Space Grotesk,sans-serif;'>
            {q_text}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── NASA ──────────────────────────────────────────────────────────────────
    if mode == "nasa":
        st.markdown(f"""
        <div style='display:flex;align-items:flex-start;gap:0.9rem;margin-bottom:1.5rem;animation:fadein 0.4s ease 0.15s both;'>
            <div style='width:36px;height:36px;min-width:36px;background:linear-gradient(135deg,#ff5722,#e64a19);
                border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:1.1rem;
                box-shadow:0 2px 10px rgba(255,87,34,0.35);margin-top:2px;'>🤖</div>
            <div style='flex:1;'>
                <div style='font-size:0.78em;font-weight:600;color:#888;margin-bottom:0.5rem;font-family:Space Mono,monospace;letter-spacing:0.04em;'>MrGPT</div>
                <div style='background:#111;border:1px solid #ff5722;border-radius:4px 18px 18px 18px;padding:1.8rem 1.5rem;
                    box-shadow:0 0 40px rgba(255,87,34,0.1),inset 0 0 40px rgba(255,87,34,0.02);'>

                    <!-- Orbital animation -->
                    <div style='position:relative;width:200px;height:200px;margin:0 auto 1.5rem;'>
                        <!-- Rings -->
                        <div style='position:absolute;top:50%;left:50%;width:180px;height:180px;
                            margin:-90px 0 0 -90px;border:1px solid rgba(255,87,34,0.2);border-radius:50%;
                            animation:spin-ring 8s linear infinite;'></div>
                        <div style='position:absolute;top:50%;left:50%;width:130px;height:130px;
                            margin:-65px 0 0 -65px;border:1px dashed rgba(255,140,0,0.25);border-radius:50%;
                            animation:spin-ring-rev 5s linear infinite;'></div>
                        <div style='position:absolute;top:50%;left:50%;width:80px;height:80px;
                            margin:-40px 0 0 -40px;border:1px solid rgba(255,200,0,0.15);border-radius:50%;
                            animation:spin-ring 3s linear infinite;'></div>
                        <!-- Center orb -->
                        <div style='position:absolute;top:50%;left:50%;width:28px;height:28px;
                            margin:-14px 0 0 -14px;background:radial-gradient(circle,#ff5722,#e64a19);
                            border-radius:50%;box-shadow:0 0 20px rgba(255,87,34,0.8);
                            animation:nasa-pulse 2s ease-in-out infinite;'></div>
                        <!-- Orbiting dots -->
                        <div style='position:absolute;top:50%;left:50%;width:10px;height:10px;margin:-5px 0 0 -5px;'>
                            <div style='width:10px;height:10px;background:#ff5722;border-radius:50%;
                                box-shadow:0 0 8px #ff5722;animation:orbit-1 3s linear infinite;'></div>
                        </div>
                        <div style='position:absolute;top:50%;left:50%;width:8px;height:8px;margin:-4px 0 0 -4px;'>
                            <div style='width:8px;height:8px;background:#ff8c00;border-radius:2px;
                                box-shadow:0 0 6px #ff8c00;animation:orbit-2 5s linear infinite;'></div>
                        </div>
                        <div style='position:absolute;top:50%;left:50%;width:6px;height:6px;margin:-3px 0 0 -3px;'>
                            <div style='width:6px;height:6px;background:#ffcc00;border-radius:50%;
                                box-shadow:0 0 6px #ffcc00;animation:orbit-3 4s linear infinite;'></div>
                        </div>
                    </div>

                    <div style='text-align:center;'>
                        <div style='font-size:0.65em;color:#ff5722;letter-spacing:0.25em;text-transform:uppercase;margin-bottom:0.5rem;font-family:Space Mono,monospace;'>◈ NEURAL ENGINE ENGAGED ◈</div>
                        <div style='font-size:1.1rem;font-weight:700;color:#e8e8e8;margin-bottom:0.2rem;font-family:Space Grotesk,sans-serif;'>{headline}</div>
                        <div style='font-size:0.85em;color:#555;font-family:Space Grotesk,sans-serif;'>{subline}</div>
                    </div>

                    <div style='margin-top:1.5rem;'>
                        <div style='display:flex;justify-content:space-between;font-size:0.65em;color:#ff5722;margin-bottom:0.4rem;font-family:Space Mono,monospace;letter-spacing:0.05em;'>
                            <span>PROCESSING SEQUENCE</span><span>T+{st.session_state.step_index * 5}s</span>
                        </div>
                        <div style='background:#0a0a0a;border:1px solid #1e1e1e;border-radius:3px;height:6px;overflow:hidden;'>
                            <div style='height:100%;background:linear-gradient(90deg,#ff5722,#ff8c00,#ffcc00);
                                animation:nasa-bar 10s ease-out forwards;
                                box-shadow:0 0 8px rgba(255,140,0,0.5);'></div>
                        </div>
                        <div style='font-size:0.65em;color:#333;margin-top:0.4rem;font-family:Space Mono,monospace;'>
                            <span style='animation:blink 0.8s infinite;display:inline-block;color:#ff5722;'>▌</span> {step}
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── CHAOS ─────────────────────────────────────────────────────────────────
    elif mode == "chaos":
        st.markdown(f"""
        <div style='display:flex;align-items:flex-start;gap:0.9rem;margin-bottom:1.5rem;animation:fadein 0.4s ease 0.15s both;'>
            <div style='width:36px;height:36px;min-width:36px;background:linear-gradient(135deg,#ff5722,#e64a19);
                border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:1.1rem;
                animation:chaos-spin 2s infinite;box-shadow:0 0 25px rgba(255,87,34,0.6);margin-top:2px;'>🤖</div>
            <div style='flex:1;'>
                <div style='font-size:0.78em;font-weight:600;color:#888;margin-bottom:0.5rem;font-family:Space Mono,monospace;animation:flicker 3s infinite;'>MrGPT</div>
                <div style='background:#1a1a1a;border:1px solid #2e2e2e;border-radius:4px 18px 18px 18px;padding:1.8rem 1.5rem;overflow:hidden;'>

                    <!-- Chaos shapes stage -->
                    <div style='position:relative;height:180px;margin-bottom:1.2rem;overflow:hidden;'>
                        <!-- Rotating triangle -->
                        <div style='position:absolute;top:30px;left:50%;margin-left:-40px;
                            width:0;height:0;
                            border-left:40px solid transparent;
                            border-right:40px solid transparent;
                            border-bottom:70px solid rgba(255,87,34,0.8);
                            filter:drop-shadow(0 0 12px rgba(255,87,34,0.6));
                            animation:chaos-fly-1 2s ease-in-out infinite;'></div>
                        <!-- Spinning square -->
                        <div style='position:absolute;top:50px;left:20%;
                            width:35px;height:35px;
                            background:rgba(255,140,0,0.7);
                            border-radius:4px;
                            box-shadow:0 0 15px rgba(255,140,0,0.5);
                            animation:chaos-fly-2 1.5s ease-in-out infinite;'></div>
                        <!-- Circle -->
                        <div style='position:absolute;top:20px;right:20%;
                            width:45px;height:45px;
                            border:3px solid rgba(255,200,0,0.7);
                            border-radius:50%;
                            box-shadow:0 0 15px rgba(255,200,0,0.4);
                            animation:chaos-fly-3 1.8s ease-in-out infinite;'></div>
                        <!-- Small dot scatter -->
                        <div style='position:absolute;top:60%;left:15%;width:8px;height:8px;background:#ff5722;border-radius:50%;animation:chaos-fly-2 1.2s ease-in-out infinite;'></div>
                        <div style='position:absolute;top:40%;right:15%;width:6px;height:6px;background:#ffcc00;border-radius:1px;animation:chaos-fly-1 0.9s ease-in-out infinite;'></div>
                        <div style='position:absolute;bottom:20px;left:40%;width:12px;height:12px;border:2px solid #ff8c00;border-radius:50%;animation:chaos-fly-3 1.4s ease-in-out infinite;'></div>
                        <!-- Glitch lines -->
                        <div style='position:absolute;top:45%;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,#ff5722,transparent);animation:flicker 0.8s infinite;'></div>
                        <div style='position:absolute;top:55%;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,#ff8c00,transparent);animation:flicker 1.2s 0.3s infinite;'></div>
                    </div>

                    <div style='text-align:center;'>
                        <div style='font-size:1.1rem;font-weight:900;color:#ff5722;text-transform:uppercase;letter-spacing:0.04em;
                            font-family:Space Grotesk,sans-serif;animation:glitch-text 3s infinite;'>{headline}</div>
                        <div style='font-size:0.85em;color:#555;margin-top:0.3rem;font-family:Space Grotesk,sans-serif;animation:flicker 4s infinite;'>{subline}</div>
                    </div>

                    <div style='background:#0e0e0e;border:1px dashed rgba(255,87,34,0.3);border-radius:6px;padding:0.7rem 0.9rem;margin-top:1.2rem;font-family:Space Mono,monospace;animation:flicker 5s infinite;'>
                        <div style='color:#ff5722;font-size:0.68em;'>
                            <span style='animation:blink 0.25s infinite;display:inline-block;'>█</span> ERROR: {step}
                        </div>
                        <div style='color:#1e1e1e;font-size:0.6em;margin-top:0.2rem;'>at NeuralEngine.process (mrgpt_core.js:847)</div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── CINEMATIC ─────────────────────────────────────────────────────────────
    else:
        st.markdown(f"""
        <div style='display:flex;align-items:flex-start;gap:0.9rem;margin-bottom:1.5rem;animation:fadein 0.5s ease 0.15s both;'>
            <div style='width:36px;height:36px;min-width:36px;background:linear-gradient(135deg,#ff5722,#e64a19);
                border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:1.1rem;
                box-shadow:0 2px 12px rgba(255,87,34,0.4);margin-top:2px;'>🤖</div>
            <div style='flex:1;'>
                <div style='font-size:0.78em;font-weight:600;color:#888;margin-bottom:0.5rem;font-family:Space Mono,monospace;'>MrGPT</div>
                <div style='background:linear-gradient(160deg,#161616,#1a1a14);border:1px solid #2a2a20;
                    border-radius:4px 18px 18px 18px;padding:2.5rem 1.5rem;text-align:center;'>

                    <!-- Cinematic floating shapes -->
                    <div style='position:relative;height:160px;margin-bottom:1.5rem;display:flex;align-items:center;justify-content:center;'>
                        <!-- Background rings -->
                        <div style='position:absolute;width:150px;height:150px;border:1px solid rgba(255,87,34,0.1);border-radius:50%;animation:spin-ring 12s linear infinite;'></div>
                        <div style='position:absolute;width:110px;height:110px;border:1px solid rgba(255,140,0,0.08);border-radius:50%;animation:spin-ring-rev 8s linear infinite;'></div>

                        <!-- Main shape: large glowing diamond -->
                        <div style='position:relative;z-index:2;
                            width:60px;height:60px;
                            background:linear-gradient(135deg,#ff5722,#ff8c00);
                            transform:rotate(45deg);
                            border-radius:6px;
                            animation:cin-float-1 4s ease-in-out infinite;
                            box-shadow:0 0 30px rgba(255,87,34,0.6),0 0 60px rgba(255,87,34,0.2);'></div>

                        <!-- Orbiting small shapes -->
                        <div style='position:absolute;top:20px;right:30%;
                            width:14px;height:14px;
                            background:rgba(255,140,0,0.6);
                            border-radius:50%;
                            animation:cin-float-2 3s ease-in-out infinite;
                            box-shadow:0 0 10px rgba(255,140,0,0.5);'></div>
                        <div style='position:absolute;bottom:25px;left:30%;
                            width:10px;height:10px;
                            border:2px solid rgba(255,200,0,0.5);
                            border-radius:2px;
                            animation:cin-float-2 5s ease-in-out 1s infinite;'></div>
                    </div>

                    <div style='font-size:1.2rem;font-weight:700;color:#e8e8e8;margin-bottom:0.4rem;
                        font-family:Space Grotesk,sans-serif;letter-spacing:-0.01em;'>{headline}</div>
                    <div style='font-size:0.85em;color:#555;animation:slow-pulse 3s ease-in-out infinite;
                        font-family:Space Grotesk,sans-serif;'>{subline}</div>

                    <div style='margin-top:1.8rem;'>
                        <div style='background:#111;border-radius:100px;height:3px;overflow:hidden;max-width:180px;margin:0 auto;'>
                            <div style='height:100%;background:linear-gradient(90deg,#ff5722,#ff8c00);
                                animation:progress-stuck 8s ease-out forwards;
                                box-shadow:0 0 6px rgba(255,87,34,0.7);'></div>
                        </div>
                        <div style='font-size:0.62em;color:#333;margin-top:0.6rem;font-family:Space Mono,monospace;animation:slow-pulse 2.5s ease-in-out infinite;'>
                            {step}
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Typing dots
    st.markdown("""
    <div style='display:flex;align-items:center;gap:0.4rem;padding:0 0 1.5rem 3.2rem;'>
        <div style='width:7px;height:7px;background:#3a3a3a;border-radius:50%;animation:pulse-dot 1.2s ease-in-out infinite;'></div>
        <div style='width:7px;height:7px;background:#3a3a3a;border-radius:50%;animation:pulse-dot 1.2s ease-in-out 0.2s infinite;'></div>
        <div style='width:7px;height:7px;background:#3a3a3a;border-radius:50%;animation:pulse-dot 1.2s ease-in-out 0.4s infinite;'></div>
        <span style='font-size:0.72em;color:#333;margin-left:0.5rem;font-family:Space Mono,monospace;'>MrGPT is thinking...</span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("← Back", use_container_width=True):
            st.session_state.page = "home"
            st.session_state.question_id = None
            st.rerun()

    time.sleep(5)
    q = get_question(st.session_state.question_id)
    if q and q["status"] == "answered":
        st.session_state.answer = q["answer"]
        st.session_state.chat_history.append({
            "question": st.session_state.question_text,
            "answer": q["answer"],
            "time": datetime.now().strftime("%H:%M"),
        })
        st.session_state.page = "answered"
        st.rerun()
    else:
        st.session_state.msg_index = (st.session_state.msg_index + 1) % len(WAITING_MESSAGES)
        st.session_state.step_index = min(st.session_state.step_index + 1, len(FAKE_STEPS) - 1)
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# ANSWERED
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "answered":
    q_text = st.session_state.question_text
    answer_text = st.session_state.answer or ""

    st.markdown(f"""
    <div style='display:flex;justify-content:flex-end;margin:2.5rem 0 1.5rem;animation:fadein 0.3s ease;'>
        <div style='background:#1e1e1e;border:1px solid #2e2e2e;border-radius:18px 18px 4px 18px;
            padding:0.9rem 1.2rem;max-width:78%;color:#e8e8e8;font-size:0.95em;line-height:1.65;
            font-family:Space Grotesk,sans-serif;'>{q_text}</div>
    </div>
    <div style='display:flex;align-items:flex-start;gap:0.9rem;margin-bottom:2.5rem;animation:fadein 0.5s ease 0.1s both;'>
        <div style='width:36px;height:36px;min-width:36px;background:linear-gradient(135deg,#ff5722,#e64a19);
            border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:1.1rem;
            box-shadow:0 2px 12px rgba(255,87,34,0.35);margin-top:2px;'>🤖</div>
        <div style='flex:1;'>
            <div style='font-size:0.78em;font-weight:600;color:#888;margin-bottom:0.6rem;font-family:Space Mono,monospace;'>MrGPT</div>
            <div style='color:#e8e8e8;font-size:0.97em;line-height:1.8;font-family:Space Grotesk,sans-serif;'>{answer_text}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("↑  Ask another question", use_container_width=True):
            st.session_state.page = "home"
            st.session_state.question_id = None
            st.session_state.question_text = ""
            st.session_state.answer = None
            st.session_state.step_index = 0
            st.rerun()

    st.markdown("""
    <div style='text-align:center;color:#222;font-size:0.7em;margin-top:2rem;font-family:Space Mono,monospace;'>
        MrGPT can make mistakes. Consider checking important info.
    </div>
    """, unsafe_allow_html=True)
