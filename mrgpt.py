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
    ("🎮", "MrGPT is playing Minecraft right now.", "He'll answer you between rounds."),
    ("💤", "MrGPT is asleep.", "His dedication to your question is truly inspiring."),
    ("🍕", "MrGPT is eating.", "Do not disturb. Seriously."),
    ("📱", "MrGPT has seen your message.", "He left it on read. Intentionally."),
    ("🏃", "MrGPT stepped outside for some air.", "In January. Without a jacket."),
    ("📺", "MrGPT is watching YouTube.", '"For research purposes."'),
    ("😤", "MrGPT is arguing with someone online.", "Your question is next. Probably."),
    ("🛁", "MrGPT is in the bathroom.", "This could take anywhere from 2 to 45 minutes."),
    ("🎵", "MrGPT is making a playlist.", "Very relevant to your question, trust."),
    ("📚", "Consulting the ancient texts.", "(It's Reddit.)"),
    ("🔋", "MrGPT battery: 2%.", "Peak performance mode activated."),
    ("🏖️", "MrGPT is mentally on vacation.", "Physically he's at his desk. Spiritually? Gone."),
    ("🤖", "BEEP BOOP PROCESSING.", "This is definitely a real AI and not a person."),
    ("🎯", "You are #1 in queue.*", "*Queue currently has 847 other questions."),
    ("🌙", "MrGPT has entered sleep mode.", "Expected wake time: unknown."),
    ("🤔", "MrGPT is thinking really hard.", "Or he forgot. Hard to tell."),
    ("⚡", "Running at 12% capacity.", "This IS peak performance."),
    ("🎲", "MrGPT rolled a die to decide if he'd answer now.", "He got a 3. Whatever that means."),
    ("🧠", "Neural pathways activating...", "Nothing is happening. We're working on it."),
    ("📡", "Transmitting your question across the servers.", "The servers are a guy named Dave."),
    ("☕", "MrGPT is getting coffee.", "Fourth cup today. He's fine."),
    ("🐌", "Answers delivered at the speed of thought.*", "*MrGPT's thoughts move quite slowly."),
    ("🔍", "Cross-referencing 47 billion data points.", "The data points are vibes."),
    ("💭", "MrGPT is pondering your question.", "He finds it deeply confusing."),
    ("🎪", "MrGPT is at a circus.", "Unclear if this is metaphorical."),
    ("🌀", "Loading...", "Has been loading since 2019."),
    ("🦆", "MrGPT is feeding ducks.", "This is relevant to your query somehow."),
    ("📉", "Processing power at historic lows.", "Please hold."),
    ("🎭", "MrGPT is in his feelings right now.", "Your question hit different."),
    ("🏋️", "MrGPT is at the gym.", "He will not be taking questions at this time."),
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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp {
    background-color: #212121;
    color: #ececec;
    font-family: 'Inter', ui-sans-serif, system-ui, sans-serif;
}

/* Hide default streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }

/* Main content area */
.block-container {
    max-width: 780px !important;
    padding: 0 1.5rem !important;
    margin: 0 auto;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #171717 !important;
    border-right: 1px solid #2f2f2f;
    min-width: 260px;
    max-width: 260px;
}
[data-testid="stSidebar"] .block-container {
    padding: 1rem 0.8rem !important;
    max-width: 100% !important;
}
[data-testid="stSidebarContent"] {
    padding: 0 !important;
}

/* Sidebar buttons */
[data-testid="stSidebar"] .stButton > button {
    background: transparent;
    color: #ababab;
    border: none;
    border-radius: 8px;
    font-size: 0.88em;
    font-weight: 400;
    padding: 0.5rem 0.8rem;
    text-align: left;
    width: 100%;
    transition: background 0.15s, color 0.15s;
    font-family: 'Inter', sans-serif;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #2a2a2a;
    color: #ececec;
}

/* Main buttons */
section.main .stButton > button {
    background: #2f2f2f;
    color: #ececec;
    border: 1px solid #424242;
    border-radius: 8px;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    font-size: 0.9em;
    padding: 0.6em 1.2em;
    transition: background 0.15s, border-color 0.15s;
    cursor: pointer;
    width: 100%;
}
section.main .stButton > button:hover {
    background: #3a3a3a;
    border-color: #555;
}

/* Textarea */
.stTextArea textarea {
    background: #2f2f2f;
    border: 1px solid #424242;
    border-radius: 16px;
    color: #ececec;
    font-family: 'Inter', sans-serif;
    font-size: 1em;
    line-height: 1.6;
    padding: 1rem 1.2rem;
    resize: none;
    transition: border-color 0.15s;
}
.stTextArea textarea:focus {
    border-color: #686868;
    box-shadow: none;
    outline: none;
}
.stTextArea textarea::placeholder { color: #555; }

/* Text input */
.stTextInput input {
    background: #2f2f2f !important;
    border: 1px solid #424242 !important;
    border-radius: 8px !important;
    color: #ececec !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput input:focus {
    border-color: #686868 !important;
    box-shadow: none !important;
}
.stTextInput input::placeholder { color: #555 !important; }

/* Containers */
[data-testid="stContainer"] {
    background: #2a2a2a;
    border: 1px solid #383838;
    border-radius: 12px;
}

/* Expander */
[data-testid="stExpander"] {
    background: #1e1e1e;
    border: 1px solid #2f2f2f;
    border-radius: 8px;
}

/* Divider */
hr { border-color: #2f2f2f !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #171717; }
::-webkit-scrollbar-thumb { background: #383838; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #4a4a4a; }

/* ── ANIMATIONS ── */
@keyframes float {
    0%,100% { transform: translateY(0); }
    50% { transform: translateY(-8px); }
}
@keyframes float-big {
    0%,100% { transform: translateY(0) scale(1); }
    50% { transform: translateY(-15px) scale(1.05); }
}
@keyframes blink {
    0%,100% { opacity: 1; }
    50% { opacity: 0; }
}
@keyframes fadein {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes progress-stuck {
    0% { width: 0%; }
    50% { width: 97%; }
    100% { width: 97%; }
}
@keyframes pulse {
    0%,100% { opacity: 0.3; transform: scale(0.8); }
    50% { opacity: 1; transform: scale(1); }
}
/* NASA mode */
@keyframes nasa-glow {
    0%,100% { text-shadow: 0 0 20px rgba(255,107,53,0.8), 0 0 40px rgba(255,107,53,0.4); }
    50% { text-shadow: 0 0 40px rgba(255,107,53,1), 0 0 80px rgba(255,69,0,0.6), 0 0 120px rgba(255,69,0,0.2); }
}
@keyframes nasa-bar {
    0% { width: 0%; }
    15% { width: 23%; }
    30% { width: 47%; }
    45% { width: 61%; }
    60% { width: 79%; }
    75% { width: 89%; }
    85% { width: 97%; }
    100% { width: 97%; }
}
@keyframes countdown {
    0% { opacity: 1; transform: scale(1.2); }
    90% { opacity: 1; transform: scale(1); }
    100% { opacity: 0; transform: scale(0.8); }
}
/* Chaos mode */
@keyframes shake {
    0%,100% { transform: translateX(0); }
    10% { transform: translateX(-8px) rotate(-2deg); }
    20% { transform: translateX(8px) rotate(2deg); }
    30% { transform: translateX(-6px) rotate(-1deg); }
    40% { transform: translateX(6px) rotate(1deg); }
    50% { transform: translateX(-4px); }
    60% { transform: translateX(4px); }
    70% { transform: translateX(-2px) rotate(-1deg); }
    80% { transform: translateX(2px) rotate(1deg); }
    90% { transform: translateX(-1px); }
}
@keyframes glitch {
    0%,100% { transform: translate(0); filter: none; }
    10% { transform: translate(-3px,1px); filter: hue-rotate(90deg); }
    20% { transform: translate(3px,-1px); filter: hue-rotate(180deg); }
    30% { transform: translate(-2px,2px); filter: none; }
    40% { transform: translate(2px,-2px); filter: hue-rotate(270deg); }
    50% { transform: translate(0); filter: none; }
    60% { transform: translate(3px,1px); filter: brightness(1.5); }
    70% { transform: translate(-3px,-1px); filter: none; }
    80% { transform: translate(1px,3px); filter: hue-rotate(45deg); }
    90% { transform: translate(-1px,-3px); filter: none; }
}
@keyframes chaos-bounce {
    0%,100% { transform: translateY(0) rotate(0deg); }
    25% { transform: translateY(-20px) rotate(-10deg); }
    50% { transform: translateY(5px) rotate(5deg); }
    75% { transform: translateY(-12px) rotate(8deg); }
}
@keyframes flicker {
    0%,100% { opacity: 1; }
    3% { opacity: 0.3; }
    6% { opacity: 1; }
    9% { opacity: 0.5; }
    12% { opacity: 1; }
    50% { opacity: 1; }
    53% { opacity: 0.2; }
    56% { opacity: 1; }
}
/* Cinematic mode */
@keyframes cinematic-enter {
    0% { opacity: 0; transform: scale(0.6); filter: blur(10px); }
    60% { opacity: 1; transform: scale(1.05); filter: blur(0); }
    100% { opacity: 1; transform: scale(1); filter: blur(0); }
}
@keyframes cinematic-float {
    0%,100% { transform: translateY(0) scale(1); filter: drop-shadow(0 0 20px rgba(255,107,53,0.4)); }
    50% { transform: translateY(-20px) scale(1.1); filter: drop-shadow(0 0 40px rgba(255,107,53,0.8)); }
}
@keyframes cinematic-text {
    0% { opacity: 0; letter-spacing: 0.5em; }
    100% { opacity: 1; letter-spacing: 0.05em; }
}
@keyframes slow-pulse {
    0%,100% { opacity: 0.6; }
    50% { opacity: 1; }
}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
defaults = {
    "page": "home",
    "question_id": None,
    "question_text": "",
    "answer": None,
    "msg_index": 0,
    "step_index": 0,
    "anim_mode": "cinematic",
    "show_admin_input": False,
    "chat_history": [],  # list of {question, answer, time}
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

params = st.query_params
is_admin = params.get("admin", "") == ADMIN_KEY

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Branding
    st.markdown("""
    <div style='padding:0.5rem 0.4rem 1rem;'>
        <div style='display:flex;align-items:center;gap:0.6rem;margin-bottom:0.2rem;'>
            <div style='
                width:28px;height:28px;
                background:linear-gradient(135deg,#ff6b35,#ff4500);
                border-radius:7px;
                display:flex;align-items:center;justify-content:center;
                font-size:0.9rem;
                flex-shrink:0;
            '>🤖</div>
            <span style='font-weight:700;font-size:1em;color:#ececec;'>MrGPT</span>
        </div>
        <div style='
            background:#2a2a2a;border:1px solid #383838;border-radius:6px;
            padding:0.3rem 0.6rem;font-size:0.72em;color:#6b6b6b;
            cursor:pointer;display:flex;justify-content:space-between;align-items:center;
        '>
            <span>MrGPT-9 Turbo Ultra Pro Max</span><span>▾</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # New chat
    if st.button("✏️  New chat", key="sb_new", use_container_width=True):
        st.session_state.page = "home"
        st.session_state.question_id = None
        st.session_state.question_text = ""
        st.session_state.answer = None
        st.rerun()

    st.markdown("<div style='height:0.3rem;'></div>", unsafe_allow_html=True)

    # About
    if st.button("ℹ️  About MrGPT", key="sb_about", use_container_width=True):
        st.session_state.page = "about"
        st.rerun()

    st.markdown("<hr style='border-color:#2a2a2a;margin:0.6rem 0;'>", unsafe_allow_html=True)

    # Chat history
    if st.session_state.chat_history:
        st.markdown("<div style='font-size:0.7em;color:#555;padding:0 0.4rem 0.4rem;text-transform:uppercase;letter-spacing:0.05em;'>Recent</div>", unsafe_allow_html=True)
        for i, chat in enumerate(reversed(st.session_state.chat_history[-8:])):
            label = chat["question"][:32] + ("…" if len(chat["question"]) > 32 else "")
            if st.button(f"💬  {label}", key=f"hist_{i}", use_container_width=True):
                st.session_state.question_text = chat["question"]
                st.session_state.answer = chat["answer"]
                st.session_state.page = "answered"
                st.rerun()
    else:
        st.markdown("<div style='font-size:0.78em;color:#3a3a3a;padding:0.4rem;text-align:center;'>No chats yet</div>", unsafe_allow_html=True)

    # Bottom: hidden admin
    st.markdown("<div style='flex:1;'></div>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color:#2a2a2a;margin:0.6rem 0;'>", unsafe_allow_html=True)

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
            st.markdown("<div style='font-size:0.75em;color:#e05;padding:0.2rem 0.4rem;'>Incorrect.</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ADMIN PAGE
# ══════════════════════════════════════════════════════════════════════════════
if is_admin or st.session_state.page == "admin_verified":
    col_back, col_title = st.columns([1, 5])
    with col_back:
        if st.button("← Back", key="admin_back"):
            st.session_state.page = "home"
            st.rerun()
    with col_title:
        st.markdown("""
        <div style='padding:0.6rem 0 1.5rem;'>
            <div style='font-size:0.72em;color:#555;margin-bottom:0.2rem;font-family:monospace;'>STAFF · MrGPT</div>
            <div style='font-size:1.4em;font-weight:700;color:#ececec;'>Inbox</div>
        </div>
        """, unsafe_allow_html=True)

    data = get_data()
    pending = [q for q in data["questions"] if q["status"] == "pending"]
    answered = [q for q in data["questions"] if q["status"] == "answered"]

    if not pending:
        st.markdown("""
        <div style='text-align:center;padding:5rem 0;color:#555;'>
            <div style='font-size:2.5rem;margin-bottom:0.8rem;'>✓</div>
            <div style='font-size:0.95em;'>All caught up. Go touch grass.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='color:#ff6b35;font-size:0.82em;font-weight:600;margin-bottom:1.2rem;letter-spacing:0.04em;'>{len(pending)} PENDING</div>", unsafe_allow_html=True)
        for q in pending:
            with st.container(border=True):
                asked_time = q["asked_at"][:16].replace("T", " at ")
                st.markdown(f"""
                <div style='font-size:0.68em;color:#555;margin-bottom:0.5rem;font-family:monospace;'>{asked_time} · #{q['id']}</div>
                <div style='font-size:1.05em;color:#ececec;margin-bottom:1rem;line-height:1.5;font-weight:500;'>"{q['question']}"</div>
                """, unsafe_allow_html=True)
                answer = st.text_area("", key=f"ans_{q['id']}", height=80,
                                      placeholder="Reply as MrGPT...", label_visibility="collapsed")
                c1, c2 = st.columns([5, 1])
                with c1:
                    if st.button("Send reply", key=f"sub_{q['id']}", use_container_width=True):
                        if answer.strip():
                            answer_question(q["id"], answer.strip())
                            st.success("Sent.")
                            time.sleep(0.6)
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
                <div style='margin-bottom:1rem;padding:0.9rem;background:#1a1a1a;border-radius:8px;'>
                    <div style='color:#555;font-size:0.82em;margin-bottom:0.4rem;'>Q: {q['question']}</div>
                    <div style='color:#ececec;font-size:0.88em;line-height:1.5;'>A: {q['answer']}</div>
                </div>
                """, unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# ABOUT PAGE
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "about":
    st.markdown("""
    <div style='padding:3rem 0 2rem;text-align:center;'>
        <div style='font-size:4rem;margin-bottom:1rem;animation:float-big 3s ease-in-out infinite;display:inline-block;'>🤖</div>
        <h1 style='font-size:2rem;font-weight:800;color:#ececec;margin-bottom:0.3rem;'>About MrGPT</h1>
        <p style='color:#555;font-size:0.9em;'>The world's most advanced AI.*</p>
        <p style='color:#2a2a2a;font-size:0.65em;'>*claims not independently verified</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:2rem;'>
        <div style='background:#2a2a2a;border:1px solid #383838;border-radius:12px;padding:1.2rem;text-align:center;'>
            <div style='font-size:2rem;font-weight:800;color:#ff6b35;'>1,847,293</div>
            <div style='font-size:0.78em;color:#6b6b6b;margin-top:0.2rem;'>Questions Answered*</div>
            <div style='font-size:0.6em;color:#2a2a2a;'>*number completely made up</div>
        </div>
        <div style='background:#2a2a2a;border:1px solid #383838;border-radius:12px;padding:1.2rem;text-align:center;'>
            <div style='font-size:2rem;font-weight:800;color:#ff6b35;'>99.7%</div>
            <div style='font-size:0.78em;color:#6b6b6b;margin-top:0.2rem;'>Accuracy Rate*</div>
            <div style='font-size:0.6em;color:#2a2a2a;'>*not measured</div>
        </div>
        <div style='background:#2a2a2a;border:1px solid #383838;border-radius:12px;padding:1.2rem;text-align:center;'>
            <div style='font-size:2rem;font-weight:800;color:#ff6b35;'>GPT-9</div>
            <div style='font-size:0.78em;color:#6b6b6b;margin-top:0.2rem;'>Model Version*</div>
            <div style='font-size:0.6em;color:#2a2a2a;'>*ahead of OpenAI by several years</div>
        </div>
        <div style='background:#2a2a2a;border:1px solid #383838;border-radius:12px;padding:1.2rem;text-align:center;'>
            <div style='font-size:2rem;font-weight:800;color:#ff6b35;'>&lt;∞</div>
            <div style='font-size:0.78em;color:#6b6b6b;margin-top:0.2rem;'>Response Time (ms)*</div>
            <div style='font-size:0.6em;color:#2a2a2a;'>*technically true</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='background:#2a2a2a;border:1px solid #383838;border-radius:12px;padding:1.5rem;margin-bottom:1.5rem;'>
        <div style='font-size:0.82em;font-weight:600;color:#ff6b35;margin-bottom:0.8rem;text-transform:uppercase;letter-spacing:0.05em;'>About Our Technology</div>
        <p style='color:#ababab;font-size:0.9em;line-height:1.7;'>MrGPT is powered by our proprietary Neural Cognition Engine™, trained on over 47 billion data points gathered from across the internet, several encyclopedias, and at least one fortune cookie.</p>
        <p style='color:#ababab;font-size:0.9em;line-height:1.7;margin-top:0.8rem;'>Our model achieves state-of-the-art results on all benchmarks we chose to include. Benchmarks that did not produce favorable results were excluded for scientific reasons.</p>
        <p style='color:#555;font-size:0.72em;margin-top:1rem;'>MrGPT Industries LLC is not responsible for any advice given, consequences thereof, or feelings of confusion. MrGPT is not affiliated with OpenAI, Google, Anthropic, or anyone with a clue.</p>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HOME PAGE
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "home":
    st.markdown("""
    <div style='text-align:center;padding:5rem 0 2rem;animation:fadein 0.4s ease;'>
        <div style='
            width:56px;height:56px;
            background:linear-gradient(135deg,#ff6b35,#ff4500);
            border-radius:14px;
            display:inline-flex;align-items:center;justify-content:center;
            font-size:1.7rem;
            margin-bottom:1.2rem;
            animation:float 3s ease-in-out infinite;
            box-shadow:0 8px 28px rgba(255,107,53,0.3);
        '>🤖</div>
        <h1 style='font-size:2.1rem;font-weight:700;color:#ececec;margin:0 0 0.5rem;letter-spacing:-0.02em;'>What can I help with?</h1>
        <p style='color:#555;font-size:0.88em;margin:0;'>Powered by MrGPT™ Neural Engine v9.4</p>
    </div>
    """, unsafe_allow_html=True)

    question = st.text_area("", placeholder="Message MrGPT...",
                             height=100, label_visibility="collapsed")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("↑  Send message", use_container_width=True):
            if question.strip():
                qid = submit_question(question.strip())
                st.session_state.question_id = qid
                st.session_state.question_text = question.strip()
                st.session_state.page = "waiting"
                st.session_state.msg_index = random.randint(0, len(WAITING_MESSAGES) - 1)
                st.session_state.step_index = 0
                st.session_state.anim_mode = random.choice(ANIM_MODES)
                st.rerun()
            else:
                st.warning("Type something first.")

    st.markdown("""
    <div style='display:flex;flex-wrap:wrap;gap:0.5rem;justify-content:center;margin-top:1.5rem;'>
        <div style='background:#2a2a2a;border:1px solid #383838;border-radius:20px;padding:0.4rem 1rem;font-size:0.82em;color:#ababab;'>✨ Explain something</div>
        <div style='background:#2a2a2a;border:1px solid #383838;border-radius:20px;padding:0.4rem 1rem;font-size:0.82em;color:#ababab;'>💡 Give me ideas</div>
        <div style='background:#2a2a2a;border:1px solid #383838;border-radius:20px;padding:0.4rem 1rem;font-size:0.82em;color:#ababab;'>🤔 Ask anything</div>
        <div style='background:#2a2a2a;border:1px solid #383838;border-radius:20px;padding:0.4rem 1rem;font-size:0.82em;color:#ababab;'>🎯 Help me decide</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align:center;margin-top:4rem;color:#333;font-size:0.72em;'>
        MrGPT can make mistakes. Consider checking important info.
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# WAITING PAGE
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "waiting":
    q_text = st.session_state.question_text
    msg = WAITING_MESSAGES[st.session_state.msg_index % len(WAITING_MESSAGES)]
    step = FAKE_STEPS[st.session_state.step_index % len(FAKE_STEPS)]
    emoji, headline, subline = msg
    mode = st.session_state.anim_mode

    # User bubble
    st.markdown(f"""
    <div style='display:flex;justify-content:flex-end;margin:2rem 0 1.5rem;animation:fadein 0.3s ease;'>
        <div style='background:#2f2f2f;border:1px solid #424242;border-radius:18px 18px 4px 18px;
            padding:0.9rem 1.2rem;max-width:80%;color:#ececec;font-size:0.95em;line-height:1.6;'>
            {q_text}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── NASA MODE ──────────────────────────────────────────────────────────────
    if mode == "nasa":
        st.markdown(f"""
        <div style='display:flex;align-items:flex-start;gap:0.8rem;margin-bottom:1.5rem;animation:fadein 0.4s ease 0.2s both;'>
            <div style='width:34px;height:34px;min-width:34px;background:linear-gradient(135deg,#ff6b35,#ff4500);
                border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:1rem;
                box-shadow:0 2px 8px rgba(255,107,53,0.3);margin-top:2px;'>🤖</div>
            <div style='flex:1;'>
                <div style='font-size:0.82em;font-weight:600;color:#ababab;margin-bottom:0.5rem;'>MrGPT</div>
                <div style='background:#1a1a1a;border:1px solid #ff4500;border-radius:4px 18px 18px 18px;padding:1.5rem;
                    box-shadow:0 0 30px rgba(255,69,0,0.15);'>

                    <div style='text-align:center;margin-bottom:1.2rem;'>
                        <div style='font-size:0.72em;color:#ff6b35;letter-spacing:0.3em;text-transform:uppercase;margin-bottom:0.5rem;animation:nasa-glow 2s ease-in-out infinite;'>
                            ◈ NEURAL ENGINE ENGAGED ◈
                        </div>
                        <div style='font-size:5rem;animation:float-big 1.5s ease-in-out infinite;display:inline-block;'>{emoji}</div>
                        <div style='font-size:1.2rem;font-weight:800;color:#ff6b35;margin-top:0.5rem;animation:nasa-glow 2s ease-in-out infinite;'>{headline}</div>
                        <div style='font-size:0.88em;color:#6b6b6b;margin-top:0.2rem;'>{subline}</div>
                    </div>

                    <div style='margin:1rem 0;'>
                        <div style='display:flex;justify-content:space-between;font-size:0.7em;color:#ff6b35;margin-bottom:0.3rem;letter-spacing:0.05em;'>
                            <span>PROCESSING SEQUENCE</span><span>T+{st.session_state.step_index * 5}s</span>
                        </div>
                        <div style='background:#0a0a0a;border:1px solid #2a2a2a;border-radius:4px;height:8px;overflow:hidden;'>
                            <div style='height:100%;width:97%;background:linear-gradient(90deg,#ff4500,#ff8c00,#ffcc00);
                                animation:nasa-bar 8s ease-out forwards;
                                box-shadow:0 0 10px rgba(255,140,0,0.5);'></div>
                        </div>
                    </div>

                    <div style='background:#0a0a0a;border:1px solid #1a1a1a;border-radius:6px;padding:0.8rem;font-family:monospace;'>
                        <div style='color:#ff4500;font-size:0.68em;margin-bottom:0.4rem;letter-spacing:0.1em;'>▶ LAUNCH_SEQUENCE.exe</div>
                        <div style='color:#ff6b35;font-size:0.72em;'>
                            <span style='animation:blink 0.7s infinite;display:inline-block;'>▌</span> {step}
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── CHAOS MODE ─────────────────────────────────────────────────────────────
    elif mode == "chaos":
        st.markdown(f"""
        <div style='display:flex;align-items:flex-start;gap:0.8rem;margin-bottom:1.5rem;animation:fadein 0.4s ease 0.2s both;'>
            <div style='width:34px;height:34px;min-width:34px;background:linear-gradient(135deg,#ff6b35,#ff4500);
                border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:1rem;
                animation:shake 0.5s infinite;box-shadow:0 0 20px rgba(255,69,0,0.5);margin-top:2px;'>🤖</div>
            <div style='flex:1;'>
                <div style='font-size:0.82em;font-weight:600;color:#ababab;margin-bottom:0.5rem;animation:flicker 3s infinite;'>MrGPT</div>
                <div style='background:#2f2f2f;border:1px solid #424242;border-radius:4px 18px 18px 18px;padding:1.5rem;animation:glitch 4s infinite;'>

                    <div style='text-align:center;margin-bottom:1rem;'>
                        <div style='font-size:5.5rem;animation:chaos-bounce 0.8s ease-in-out infinite;display:inline-block;'>{emoji}</div>
                        <div style='font-size:1.15rem;font-weight:900;color:#ff4500;margin-top:0.3rem;animation:flicker 2s infinite;text-transform:uppercase;letter-spacing:0.05em;'>
                            {headline}
                        </div>
                        <div style='font-size:0.85em;color:#6b6b6b;margin-top:0.3rem;'>{subline}</div>
                    </div>

                    <div style='background:#1a1a1a;border:1px dashed #ff4500;border-radius:4px;padding:0.7rem;margin-top:0.8rem;font-family:monospace;animation:flicker 4s infinite;'>
                        <div style='color:#ff4500;font-size:0.72em;'>
                            <span style='animation:blink 0.3s infinite;display:inline-block;'>█</span> ERROR: {step}
                        </div>
                        <div style='color:#333;font-size:0.65em;margin-top:0.3rem;'>stack trace: [REDACTED] [REDACTED] [REDACTED]</div>
                    </div>

                    <div style='display:flex;justify-content:center;gap:0.4rem;margin-top:1rem;'>
                        <div style='width:10px;height:10px;background:#ff4500;border-radius:50%;animation:pulse 0.4s ease-in-out infinite;'></div>
                        <div style='width:10px;height:10px;background:#ff6b35;border-radius:50%;animation:pulse 0.4s ease-in-out 0.15s infinite;'></div>
                        <div style='width:10px;height:10px;background:#ff8c00;border-radius:50%;animation:pulse 0.4s ease-in-out 0.3s infinite;'></div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── CINEMATIC MODE ─────────────────────────────────────────────────────────
    else:
        st.markdown(f"""
        <div style='display:flex;align-items:flex-start;gap:0.8rem;margin-bottom:1.5rem;animation:fadein 0.5s ease 0.2s both;'>
            <div style='width:34px;height:34px;min-width:34px;background:linear-gradient(135deg,#ff6b35,#ff4500);
                border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:1rem;
                box-shadow:0 2px 8px rgba(255,107,53,0.3);margin-top:2px;'>🤖</div>
            <div style='flex:1;'>
                <div style='font-size:0.82em;font-weight:600;color:#ababab;margin-bottom:0.5rem;'>MrGPT</div>
                <div style='background:linear-gradient(135deg,#1e1e1e,#252520);border:1px solid #383830;
                    border-radius:4px 18px 18px 18px;padding:2rem;text-align:center;'>
                    <div style='font-size:6rem;animation:cinematic-float 3s ease-in-out infinite;display:inline-block;
                        filter:drop-shadow(0 0 30px rgba(255,107,53,0.5));'>{emoji}</div>
                    <div style='font-size:1.1rem;font-weight:600;color:#ececec;margin:1rem 0 0.3rem;
                        animation:cinematic-text 1s ease-out both;'>{headline}</div>
                    <div style='font-size:0.85em;color:#6b6b6b;animation:slow-pulse 3s ease-in-out infinite;'>{subline}</div>

                    <div style='margin-top:1.5rem;'>
                        <div style='background:#1a1a1a;border-radius:100px;height:4px;overflow:hidden;max-width:200px;margin:0 auto;'>
                            <div style='height:100%;width:97%;background:linear-gradient(90deg,#ff6b35,#ff8c00);
                                animation:progress-stuck 6s ease-out forwards;
                                box-shadow:0 0 8px rgba(255,107,53,0.6);'></div>
                        </div>
                        <div style='font-size:0.68em;color:#333;margin-top:0.5rem;animation:slow-pulse 2s ease-in-out infinite;'>
                            {step}
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Typing dots
    st.markdown("""
    <div style='display:flex;align-items:center;gap:0.4rem;padding:0 0 1.5rem 3rem;'>
        <div style='width:7px;height:7px;background:#555;border-radius:50%;animation:pulse 1.2s ease-in-out infinite;'></div>
        <div style='width:7px;height:7px;background:#555;border-radius:50%;animation:pulse 1.2s ease-in-out 0.2s infinite;'></div>
        <div style='width:7px;height:7px;background:#555;border-radius:50%;animation:pulse 1.2s ease-in-out 0.4s infinite;'></div>
        <span style='font-size:0.75em;color:#444;margin-left:0.5rem;'>MrGPT is thinking...</span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("← Back", use_container_width=True):
            st.session_state.page = "home"
            st.session_state.question_id = None
            st.rerun()

    # Poll
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
# ANSWERED PAGE
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "answered":
    q_text = st.session_state.question_text
    answer_text = st.session_state.answer or ""

    st.markdown(f"""
    <div style='display:flex;justify-content:flex-end;margin:2rem 0 1.5rem;animation:fadein 0.3s ease;'>
        <div style='background:#2f2f2f;border:1px solid #424242;border-radius:18px 18px 4px 18px;
            padding:0.9rem 1.2rem;max-width:80%;color:#ececec;font-size:0.95em;line-height:1.6;'>
            {q_text}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style='display:flex;align-items:flex-start;gap:0.8rem;margin-bottom:2rem;animation:fadein 0.5s ease 0.1s both;'>
        <div style='width:34px;height:34px;min-width:34px;background:linear-gradient(135deg,#ff6b35,#ff4500);
            border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:1rem;
            box-shadow:0 2px 8px rgba(255,107,53,0.3);margin-top:2px;'>🤖</div>
        <div style='flex:1;'>
            <div style='font-size:0.82em;font-weight:600;color:#ababab;margin-bottom:0.5rem;'>MrGPT</div>
            <div style='color:#ececec;font-size:0.97em;line-height:1.8;'>{answer_text}</div>
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
    <div style='text-align:center;color:#333;font-size:0.72em;margin-top:2rem;'>
        MrGPT can make mistakes. Consider checking important info.
    </div>
    """, unsafe_allow_html=True)
