import streamlit as st
import requests
import json
import random
import time
import uuid
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
JSONBIN_API_KEY = os.getenv("JSONBIN_API_KEY", "")
JSONBIN_BIN_ID  = os.getenv("JSONBIN_BIN_ID", "")
ADMIN_KEY       = os.getenv("ADMIN_KEY", "admin123")
JSONBIN_URL     = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}"
HEADERS         = {"X-Master-Key": JSONBIN_API_KEY, "Content-Type": "application/json"}

# ── Funny content ─────────────────────────────────────────────────────────────
WAITING_MESSAGES = [
    ("🎮", "mrGPT is playing Minecraft right now.", "He'll answer you between rounds."),
    ("💤", "mrGPT is asleep.", "His dedication to your question is truly inspiring."),
    ("🍕", "mrGPT is eating.", "Do not disturb. Seriously."),
    ("📱", "mrGPT has seen your message.", "He left it on read. Intentionally."),
    ("🏃", "mrGPT stepped outside for some air.", "In January. Without a jacket."),
    ("📺", "mrGPT is watching YouTube.", '"For research purposes."'),
    ("😤", "mrGPT is arguing with someone online.", "Your question is next. Probably."),
    ("🛁", "mrGPT is in the bathroom.", "This could take anywhere from 2 to 45 minutes."),
    ("🎵", "mrGPT is making a playlist.", "Very relevant to your question, trust."),
    ("📚", "Consulting the ancient texts.", "(It's Reddit.)"),
    ("🔋", "mrGPT battery: 2%.", "Peak performance mode activated."),
    ("🏖️", "mrGPT is mentally on vacation.", "Physically he's at his desk. Spiritually? Gone."),
    ("🤖", "BEEP BOOP PROCESSING.", "This is definitely a real AI and not a person."),
    ("🎯", "You are #1 in queue.*", "*Queue currently has 847 other questions."),
    ("🌙", "mrGPT has entered sleep mode.", "Expected wake time: unknown."),
    ("🤔", "mrGPT is thinking really hard.", "Or he forgot. Hard to tell."),
    ("⚡", "Running at 12% capacity.", "This IS peak performance."),
    ("🎲", "mrGPT rolled a die to decide if he'd answer now.", "He got a 3. Whatever that means."),
    ("🧠", "Neural pathways activating...", "Nothing is happening. We're working on it."),
    ("📡", "Transmitting your question across the servers.", "The servers are a guy named Dave."),
    ("☕", "mrGPT is getting coffee.", "Fourth cup today. He's fine."),
    ("🐌", "Answers delivered at the speed of thought.*", "*mrGPT's thoughts move quite slowly."),
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
    "Finalizing neural output...",
    "97% complete...",
    "97% complete...",
    "97% complete...",
    "97% complete...",
    "Still 97%... this is normal...",
]

# ── Storage helpers ────────────────────────────────────────────────────────────
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
    qid = str(uuid.uuid4())[:8]
    data["questions"].append({
        "id": qid,
        "question": question_text,
        "answer": None,
        "status": "pending",
        "asked_at": datetime.now().isoformat(),
        "answered_at": None,
    })
    save_data(data)
    return qid

def get_question(qid):
    data = get_data()
    for q in data["questions"]:
        if q["id"] == qid:
            return q
    return None

def answer_question(qid, answer_text):
    data = get_data()
    for q in data["questions"]:
        if q["id"] == qid:
            q["answer"] = answer_text
            q["status"] = "answered"
            q["answered_at"] = datetime.now().isoformat()
            break
    save_data(data)

def delete_question(qid):
    data = get_data()
    data["questions"] = [q for q in data["questions"] if q["id"] != qid]
    save_data(data)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="mrGPT", page_icon="🤖", layout="centered")

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&family=JetBrains+Mono:wght@400;700&display=swap');

/* Reset */
.stApp { background: #07070f; color: #e0e0f0; font-family: 'Inter', sans-serif; }
.block-container { max-width: 720px; padding-top: 2rem; }

/* Hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }

/* Sidebar hidden unless admin */
[data-testid="stSidebar"] { display: none; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #4f46e5);
    color: white;
    border: none;
    border-radius: 10px;
    font-family: 'Inter', sans-serif;
    font-weight: 700;
    font-size: 1em;
    padding: 0.6em 1.4em;
    transition: all 0.2s;
    letter-spacing: 0.02em;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #8b5cf6, #6366f1);
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(124,58,237,0.4);
}

/* Text input */
.stTextArea textarea, .stTextInput input {
    background: #12121f;
    border: 1.5px solid #2d2b55;
    border-radius: 10px;
    color: #e0e0f0;
    font-family: 'Inter', sans-serif;
    font-size: 1em;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: #7c3aed;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.2);
}

/* Containers */
[data-testid="stContainer"] {
    background: #0e0e1f;
    border: 1px solid #1e1e40;
    border-radius: 14px;
    padding: 1rem;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #07070f; }
::-webkit-scrollbar-thumb { background: #7c3aed; border-radius: 2px; }

/* Typography */
h1,h2,h3 { font-family: 'Inter', sans-serif; }

/* Progress bar override */
.stProgress > div > div { background: linear-gradient(90deg, #7c3aed, #f97316); }

/* Glitch animation */
@keyframes glitch {
    0%   { transform: translate(0); }
    20%  { transform: translate(-2px, 1px); }
    40%  { transform: translate(2px, -1px); }
    60%  { transform: translate(-1px, 2px); }
    80%  { transform: translate(1px, -2px); }
    100% { transform: translate(0); }
}
@keyframes pulse-glow {
    0%,100% { text-shadow: 0 0 10px rgba(124,58,237,0.6); }
    50%      { text-shadow: 0 0 30px rgba(249,115,22,0.8), 0 0 60px rgba(124,58,237,0.4); }
}
@keyframes blink {
    0%,100% { opacity: 1; }
    50%      { opacity: 0; }
}
@keyframes spin-slow {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
}
@keyframes typewriter {
    from { width: 0; }
    to   { width: 100%; }
}
@keyframes float {
    0%,100% { transform: translateY(0px); }
    50%      { transform: translateY(-8px); }
}
@keyframes progress-stuck {
    0%   { width: 0%; }
    70%  { width: 97%; }
    100% { width: 97%; }
}
@keyframes scanline {
    0%   { top: -100%; }
    100% { top: 100%; }
}
@keyframes reveal-flash {
    0%   { background: #7c3aed; opacity:0.8; }
    100% { background: transparent; opacity:0; }
}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in [("page","home"),("question_id",None),("question_text",""),
             ("answer",None),("msg_index",0),("step_index",0)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Admin check ───────────────────────────────────────────────────────────────
params = st.query_params
is_admin = params.get("admin", "") == ADMIN_KEY

# ══════════════════════════════════════════════════════════════════════════════
#  ADMIN PAGE
# ══════════════════════════════════════════════════════════════════════════════
if is_admin:
    st.markdown("""
    <div style='text-align:center;margin-bottom:1.5rem;'>
        <div style='font-family:JetBrains Mono,monospace;color:#f97316;font-size:0.8em;letter-spacing:0.2em;'>ADMIN PANEL // AUTHORIZED ACCESS</div>
        <h2 style='color:#e0e0f0;margin:0.3rem 0;'>🤖 mrGPT Control Room</h2>
        <div style='color:#6b6b9a;font-size:0.85em;'>You are the AI. No pressure.</div>
    </div>
    """, unsafe_allow_html=True)

    data = get_data()
    pending = [q for q in data["questions"] if q["status"] == "pending"]
    answered = [q for q in data["questions"] if q["status"] == "answered"]

    if not pending:
        st.markdown("""
        <div style='text-align:center;padding:3rem;color:#6b6b9a;'>
            <div style='font-size:3rem;'>🎉</div>
            <div style='font-size:1.1em;margin-top:0.5rem;'>No pending questions.</div>
            <div style='font-size:0.85em;margin-top:0.3rem;'>Go touch grass.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='color:#f97316;font-weight:700;margin-bottom:1rem;'>📬 {len(pending)} question(s) waiting for your genius</div>", unsafe_allow_html=True)
        for q in pending:
            with st.container(border=True):
                asked_time = q["asked_at"][:16].replace("T", " at ")
                st.markdown(f"""
                <div style='font-size:0.72em;color:#6b6b9a;margin-bottom:0.4rem;font-family:JetBrains Mono,monospace;'>ID: {q['id']} // Asked: {asked_time}</div>
                <div style='font-size:1.1em;font-weight:700;color:#e0e0f0;margin-bottom:1rem;'>"{q['question']}"</div>
                """, unsafe_allow_html=True)
                answer = st.text_area("Your answer:", key=f"ans_{q['id']}", height=100,
                                       placeholder="Type your incredibly intelligent AI response here...")
                col1, col2 = st.columns([3,1])
                with col1:
                    if st.button("📤 Send Answer", key=f"sub_{q['id']}", use_container_width=True):
                        if answer.strip():
                            answer_question(q["id"], answer.strip())
                            st.success("✅ Answer sent! The human on the other end will never know.")
                            time.sleep(1)
                            st.rerun()
                with col2:
                    if st.button("🗑️ Delete", key=f"del_{q['id']}", use_container_width=True):
                        delete_question(q["id"])
                        st.rerun()

    if answered:
        st.markdown("---")
        with st.expander(f"📜 Answered questions ({len(answered)})"):
            for q in reversed(answered[-10:]):
                st.markdown(f"""
                <div style='margin-bottom:1rem;padding:0.8rem;background:#0a0a1a;border-radius:8px;border-left:3px solid #7c3aed;'>
                    <div style='color:#a0a0c0;font-size:0.85em;margin-bottom:0.3rem;'>Q: {q['question']}</div>
                    <div style='color:#e0e0f0;font-size:0.9em;'>A: {q['answer']}</div>
                </div>
                """, unsafe_allow_html=True)

    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
#  PUBLIC: HOME PAGE
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "home":
    st.markdown("""
    <div style='text-align:center;padding:2rem 0 1rem;'>
        <div style='font-size:4.5rem;animation:float 3s ease-in-out infinite;display:inline-block;'>🤖</div>
        <h1 style='
            font-size:3.2rem;
            font-weight:900;
            background:linear-gradient(135deg,#7c3aed,#f97316,#7c3aed);
            background-size:200%;
            -webkit-background-clip:text;
            -webkit-text-fill-color:transparent;
            animation:pulse-glow 2s ease-in-out infinite;
            margin:0.3rem 0 0;
            letter-spacing:-0.02em;
        '>mrGPT</h1>
        <div style='color:#6b6b9a;font-size:0.9em;margin-top:0.2rem;letter-spacing:0.05em;'>
            POWERED BY NEURAL NETWORKS™ &nbsp;·&nbsp; 100% ARTIFICIAL &nbsp;·&nbsp; 0% INTELLIGENT
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Fake stats bar
    st.markdown("""
    <div style='
        display:flex;justify-content:center;gap:2.5rem;
        padding:0.8rem;margin:1rem 0;
        background:#0e0e1f;border:1px solid #1e1e40;border-radius:10px;
        font-size:0.78em;color:#6b6b9a;text-align:center;
    '>
        <div><div style='color:#f97316;font-weight:700;font-size:1.3em;'>1,847,293</div>Questions Answered</div>
        <div><div style='color:#7c3aed;font-weight:700;font-size:1.3em;'>99.7%</div>Accuracy*</div>
        <div><div style='color:#f97316;font-weight:700;font-size:1.3em;'>&lt;∞ms</div>Response Time</div>
        <div><div style='color:#7c3aed;font-weight:700;font-size:1.3em;'>GPT-9</div>Model Version</div>
    </div>
    <div style='text-align:right;color:#2d2b55;font-size:0.65em;margin-top:-0.8rem;margin-bottom:0.5rem;'>*accuracy not verified or verifiable</div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='margin:1.5rem 0 0.5rem;font-weight:700;font-size:1.05em;'>Ask mrGPT anything:</div>", unsafe_allow_html=True)
    question = st.text_area("", placeholder="What is the meaning of life? Why is the sky blue? What should I eat for dinner?",
                              height=110, label_visibility="collapsed")

    # Disclaimer
    st.markdown("""
    <div style='font-size:0.72em;color:#2d2b55;margin:0.3rem 0 1rem;font-family:JetBrains Mono,monospace;'>
        By submitting, you agree that mrGPT is not responsible for any advice given, 
        consequences of following said advice, existential crises, or 
        feelings of confusion. mrGPT's responses are for entertainment only.
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("🚀 Ask mrGPT", use_container_width=True):
            if question.strip():
                with st.spinner("Submitting to the neural network..."):
                    qid = submit_question(question.strip())
                st.session_state.question_id = qid
                st.session_state.question_text = question.strip()
                st.session_state.page = "waiting"
                st.session_state.msg_index = random.randint(0, len(WAITING_MESSAGES)-1)
                st.session_state.step_index = 0
                st.rerun()
            else:
                st.error("Please type a question. mrGPT can't read minds. Yet.")

    st.markdown("""
    <div style='text-align:center;margin-top:2.5rem;color:#1e1e40;font-size:0.75em;font-family:JetBrains Mono,monospace;'>
        mrGPT v9.4.2-beta // NOT affiliated with OpenAI, Google, Anthropic, or anyone competent
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  PUBLIC: WAITING PAGE
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "waiting":
    msg = WAITING_MESSAGES[st.session_state.msg_index % len(WAITING_MESSAGES)]
    step = FAKE_STEPS[st.session_state.step_index % len(FAKE_STEPS)]
    emoji, headline, subline = msg

    st.markdown(f"""
    <div style='text-align:center;padding:1.5rem 0;'>
        <div style='font-size:5rem;animation:float 2s ease-in-out infinite;display:inline-block;'>{emoji}</div>
        <h2 style='color:#f97316;font-size:1.6rem;font-weight:800;margin:0.5rem 0 0.2rem;'>{headline}</h2>
        <div style='color:#9090b0;font-size:1rem;'>{subline}</div>
    </div>
    """, unsafe_allow_html=True)

    # Question recap
    q_text = st.session_state.question_text
    st.markdown(f"""
    <div style='
        background:#0e0e1f;border:1px solid #2d2b55;border-radius:10px;
        padding:1rem 1.2rem;margin:0.5rem 0 1.2rem;
    '>
        <div style='font-size:0.72em;color:#6b6b9a;font-family:JetBrains Mono,monospace;margin-bottom:0.3rem;'>YOUR QUESTION:</div>
        <div style='color:#e0e0f0;font-size:1em;'>"{q_text}"</div>
    </div>
    """, unsafe_allow_html=True)

    # Fake progress bar
    st.markdown("""
    <div style='margin:0.5rem 0;'>
        <div style='font-size:0.72em;color:#6b6b9a;font-family:JetBrains Mono,monospace;margin-bottom:0.4rem;'>PROCESSING PROGRESS:</div>
        <div style='background:#12121f;border-radius:6px;height:12px;overflow:hidden;border:1px solid #1e1e40;'>
            <div style='
                height:100%;width:97%;
                background:linear-gradient(90deg,#7c3aed,#f97316);
                animation:progress-stuck 3s ease-out forwards;
                border-radius:6px;
            '></div>
        </div>
        <div style='text-align:right;font-size:0.7em;color:#6b6b9a;font-family:JetBrains Mono,monospace;margin-top:0.2rem;'>97% — almost there (has been saying this for a while)</div>
    </div>
    """, unsafe_allow_html=True)

    # Fake AI steps
    st.markdown(f"""
    <div style='
        background:#070714;border:1px solid #1a1a35;border-radius:8px;
        padding:0.8rem 1rem;margin:0.8rem 0;
        font-family:JetBrains Mono,monospace;font-size:0.75em;color:#4a4a7a;
    '>
        <div style='color:#7c3aed;margin-bottom:0.4rem;'>▶ mrGPT_engine.exe</div>
        {"".join(f'<div style="color:#2d4a2d;">✓ {FAKE_STEPS[i]}</div>' for i in range(min(st.session_state.step_index, 9)))}
        <div style='color:#f97316;'>
            <span style='animation:blink 0.8s infinite;display:inline-block;'>▌</span>
            {step}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Timer note
    st.markdown(f"""
    <div style='text-align:center;color:#3a3a5a;font-size:0.75em;font-family:JetBrains Mono,monospace;margin-top:0.8rem;'>
        Auto-checking for answer every 5 seconds... // ID: {st.session_state.question_id}
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2,1,2])
    with col2:
        if st.button("✕ Cancel", use_container_width=True):
            if st.session_state.question_id:
                delete_question(st.session_state.question_id)
            st.session_state.page = "home"
            st.session_state.question_id = None
            st.rerun()

    # Poll for answer
    time.sleep(5)
    q = get_question(st.session_state.question_id)
    if q and q["status"] == "answered":
        st.session_state.answer = q["answer"]
        st.session_state.page = "answered"
        st.rerun()
    else:
        # Cycle messages and steps
        st.session_state.msg_index = (st.session_state.msg_index + 1) % len(WAITING_MESSAGES)
        st.session_state.step_index = min(st.session_state.step_index + 1, len(FAKE_STEPS) - 1)
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  PUBLIC: ANSWERED PAGE
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "answered":
    st.markdown("""
    <div style='text-align:center;padding:1rem 0 0.5rem;'>
        <div style='
            display:inline-block;
            background:linear-gradient(135deg,#7c3aed22,#f9731622);
            border:1px solid #7c3aed;
            border-radius:10px;
            padding:0.3rem 1rem;
            font-family:JetBrains Mono,monospace;
            font-size:0.75em;
            color:#7c3aed;
            letter-spacing:0.15em;
            margin-bottom:0.8rem;
        '>◈ NEURAL RESPONSE RECEIVED ◈</div>
        <h2 style='
            color:#f97316;
            font-size:2rem;
            font-weight:900;
            text-shadow:0 0 20px rgba(249,115,22,0.5);
            margin:0.2rem 0;
        '>mrGPT has spoken.</h2>
        <div style='color:#6b6b9a;font-size:0.85em;'>After extensive deliberation and zero hesitation.</div>
    </div>
    """, unsafe_allow_html=True)

    q_text = st.session_state.question_text
    st.markdown(f"""
    <div style='background:#0a0a1a;border-radius:10px;padding:0.8rem 1.2rem;margin:0.8rem 0;border-left:3px solid #6b6b9a;'>
        <div style='font-size:0.7em;color:#4a4a7a;font-family:JetBrains Mono,monospace;margin-bottom:0.3rem;'>QUERY:</div>
        <div style='color:#a0a0c0;font-size:0.95em;'>"{q_text}"</div>
    </div>
    """, unsafe_allow_html=True)

    answer_text = st.session_state.answer or ""
    st.markdown(f"""
    <div style='
        background:linear-gradient(135deg,#0e0a1f,#1a0e10);
        border:1px solid rgba(124,58,237,0.4);
        border-radius:14px;
        padding:1.5rem;
        margin:0.5rem 0 1.2rem;
        position:relative;
        overflow:hidden;
    '>
        <div style='
            position:absolute;top:0;left:0;right:0;bottom:0;
            background:linear-gradient(135deg,rgba(124,58,237,0.03),rgba(249,115,22,0.03));
            pointer-events:none;
        '></div>
        <div style='font-size:0.7em;color:#7c3aed;font-family:JetBrains Mono,monospace;margin-bottom:0.6rem;letter-spacing:0.1em;'>▶ mrGPT RESPONSE:</div>
        <div style='color:#e8e8ff;font-size:1.1em;line-height:1.7;font-weight:500;'>{answer_text}</div>
        <div style='text-align:right;margin-top:1rem;font-size:0.65em;color:#3a3a5a;font-family:JetBrains Mono,monospace;'>
            Generated by mrGPT™ Neural Engine v9.4.2 // Confidence: extremely high
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Fake accuracy note
    st.markdown("""
    <div style='
        text-align:center;font-size:0.72em;color:#3a3a5a;
        font-family:JetBrains Mono,monospace;margin-bottom:1.2rem;
    '>
        ⚠ mrGPT responses are 99.7% accurate* &nbsp;·&nbsp; *figure entirely made up
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("🔄 Ask Another Question", use_container_width=True):
            st.session_state.page = "home"
            st.session_state.question_id = None
            st.session_state.question_text = ""
            st.session_state.answer = None
            st.session_state.step_index = 0
            st.rerun()

    st.markdown("""
    <div style='text-align:center;margin-top:1rem;'>
        <div style='font-size:0.75em;color:#2d2b55;'>mrGPT is not responsible for any decisions made based on this response.</div>
        <div style='font-size:0.7em;color:#1e1e40;margin-top:0.2rem;'>This has been a production of mrGPT Industries™. All rights reserved. Or whatever.</div>
    </div>
    """, unsafe_allow_html=True)
