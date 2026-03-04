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
MAX_QUESTIONS   = 3

WAITING_MESSAGES = [
    ("🎮", "MrGPT is playing Minecraft right now.", "He'll get to you between rounds."),
    ("💤", "MrGPT is asleep.", "His dedication to your question is truly inspiring."),
    ("🍕", "MrGPT is eating.", "Do not disturb. Seriously."),
    ("📱", "MrGPT has seen your message.", "He left it on read. Intentionally."),
    ("🏃", "MrGPT stepped outside for some air.", "In January. Without a jacket."),
    ("📺", "MrGPT is watching YouTube.", '"For research purposes."'),
    ("😤", "MrGPT is arguing with someone online.", "Your question is next. Probably."),
    ("🛁", "MrGPT is in the bathroom.", "This could take 2 to 45 minutes."),
    ("🎵", "MrGPT is making a playlist.", "Very relevant to your question, trust."),
    ("📚", "Consulting the ancient texts.", "(It's Reddit.)"),
    ("🔋", "MrGPT battery: 2%.", "Peak performance mode activated."),
    ("🏖️", "MrGPT is mentally on vacation.", "Physically he's at his desk. Spiritually? Gone."),
    ("🎯", "You are #1 in queue.", "(Queue has 847 other questions.)"),
    ("🌙", "MrGPT has entered sleep mode.", "Expected wake time: unknown."),
    ("🤔", "MrGPT is thinking really hard.", "Or he forgot. Hard to tell."),
    ("🎲", "MrGPT rolled a die to decide.", "He got a 3. Whatever that means."),
    ("☕", "MrGPT is getting coffee.", "Fourth cup today. He's fine."),
    ("🐌", "Processing at full speed.", "(Full speed is relative.)"),
]

FAKE_STEPS = [
    "Tokenizing input vectors...",
    "Loading language model weights...",
    "Running attention layers...",
    "Cross-referencing knowledge base...",
    "Performing semantic analysis...",
    "Optimizing response...",
    "Finalizing output...",
    "97% complete...",
    "97% complete...",
    "97% complete...",
    "Still at 97%... this is normal...",
]

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
    # Keep only the most recent MAX_QUESTIONS
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

st.set_page_config(page_title="MrGPT", page_icon="🤖", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, .stApp {
    background-color: #0f0f0f;
    color: #ececec;
    font-family: 'Inter', sans-serif;
}
.block-container {
    max-width: 680px;
    padding-top: 4rem;
    padding-bottom: 4rem;
}
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebar"] { display: none; }

.stButton > button {
    background: #1a1a1a;
    color: #ececec;
    border: 1px solid #333;
    border-radius: 8px;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    font-size: 0.95em;
    padding: 0.55em 1.4em;
    transition: all 0.15s;
    width: 100%;
}
.stButton > button:hover {
    background: #242424;
    border-color: #555;
}

.stTextArea textarea {
    background: #161616;
    border: 1px solid #2a2a2a;
    border-radius: 12px;
    color: #ececec;
    font-family: 'Inter', sans-serif;
    font-size: 1em;
    padding: 1rem;
    resize: none;
    transition: border-color 0.15s;
}
.stTextArea textarea:focus {
    border-color: #ff4500;
    box-shadow: 0 0 0 3px rgba(255,69,0,0.1);
    outline: none;
}
.stTextArea textarea::placeholder { color: #444; }

.stTextInput input {
    background: #161616;
    border: 1px solid #2a2a2a;
    border-radius: 8px;
    color: #ececec;
    font-family: 'Inter', sans-serif;
    font-size: 0.95em;
    letter-spacing: 0.05em;
}
.stTextInput input:focus {
    border-color: #ff4500;
    box-shadow: 0 0 0 3px rgba(255,69,0,0.1);
}
.stTextInput input::placeholder { color: #444; }

[data-testid="stContainer"] {
    background: #161616;
    border: 1px solid #222;
    border-radius: 12px;
}

.stProgress > div > div {
    background: linear-gradient(90deg, #ff4500, #ff8c00);
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0f0f0f; }
::-webkit-scrollbar-thumb { background: #333; border-radius: 2px; }

@keyframes float {
    0%,100% { transform: translateY(0); }
    50% { transform: translateY(-6px); }
}
@keyframes blink {
    0%,100% { opacity: 1; }
    50% { opacity: 0; }
}
@keyframes progress-stuck {
    0% { width: 0%; }
    60% { width: 97%; }
    100% { width: 97%; }
}
@keyframes fadein {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>
""", unsafe_allow_html=True)

for k, v in [("page","home"),("question_id",None),("question_text",""),
             ("answer",None),("msg_index",0),("step_index",0),
             ("show_admin_input",False),("show_check",False)]:
    if k not in st.session_state:
        st.session_state[k] = v

params = st.query_params
is_admin = params.get("admin", "") == ADMIN_KEY

# ── ADMIN PAGE ────────────────────────────────────────────────────────────────
if is_admin or st.session_state.page == "admin_verified":
    st.markdown("""
    <div style='margin-bottom:2rem;'>
        <div style='font-size:0.75em;color:#555;margin-bottom:0.3rem;'>MrGPT — Staff Panel</div>
        <div style='font-size:1.4em;font-weight:600;color:#ececec;'>Inbox</div>
    </div>
    """, unsafe_allow_html=True)

    data = get_data()
    pending = [q for q in data["questions"] if q["status"] == "pending"]
    answered = [q for q in data["questions"] if q["status"] == "answered"]

    if not pending:
        st.markdown("""
        <div style='text-align:center;padding:4rem 0;color:#444;'>
            <div style='font-size:2rem;margin-bottom:0.8rem;'>✓</div>
            <div>No pending questions.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='color:#ff4500;font-size:0.85em;font-weight:500;margin-bottom:1rem;'>{len(pending)} waiting</div>", unsafe_allow_html=True)
        for q in pending:
            with st.container(border=True):
                asked_time = q["asked_at"][:16].replace("T", " at ")
                st.markdown(f"""
                <div style='font-size:0.7em;color:#444;margin-bottom:0.5rem;font-family:monospace;'>{asked_time} · #{q['id']}</div>
                <div style='font-size:1.05em;color:#ececec;margin-bottom:1rem;font-weight:500;'>"{q['question']}"</div>
                """, unsafe_allow_html=True)
                answer = st.text_area("", key=f"ans_{q['id']}", height=90,
                                      placeholder="Type your response...", label_visibility="collapsed")
                col1, col2 = st.columns([4,1])
                with col1:
                    if st.button("Send", key=f"sub_{q['id']}", use_container_width=True):
                        if answer.strip():
                            answer_question(q["id"], answer.strip())
                            st.success("Sent.")
                            time.sleep(0.8)
                            st.rerun()
                with col2:
                    if st.button("✕", key=f"del_{q['id']}", use_container_width=True):
                        delete_question(q["id"])
                        st.rerun()

    if answered:
        st.markdown("---")
        with st.expander(f"History ({len(answered)})"):
            for q in reversed(answered):
                st.markdown(f"""
                <div style='margin-bottom:1rem;padding:0.8rem;background:#111;border-radius:8px;border-left:2px solid #333;'>
                    <div style='color:#666;font-size:0.82em;margin-bottom:0.3rem;'>Q: {q['question']}</div>
                    <div style='color:#ececec;font-size:0.88em;'>A: {q['answer']}</div>
                </div>
                """, unsafe_allow_html=True)
    st.stop()

# ── HOME PAGE ─────────────────────────────────────────────────────────────────
if st.session_state.page == "home":
    st.markdown("""
    <div style='text-align:center;padding:3rem 0 2.5rem;animation:fadein 0.4s ease;'>
        <div style='font-size:3rem;margin-bottom:1rem;animation:float 3s ease-in-out infinite;display:inline-block;'>🤖</div>
        <h1 style='font-size:2.6rem;font-weight:700;color:#ececec;margin:0 0 0.4rem;letter-spacing:-0.02em;'>MrGPT</h1>
        <p style='color:#555;font-size:0.95em;margin:0;font-weight:400;'>Ask anything. Get an answer.</p>
    </div>
    """, unsafe_allow_html=True)

    question = st.text_area("", placeholder="Ask MrGPT anything...",
                             height=120, label_visibility="collapsed")

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("Ask MrGPT", use_container_width=True):
            if question.strip():
                qid = submit_question(question.strip())
                st.session_state.question_id = qid
                st.session_state.question_text = question.strip()
                st.session_state.page = "waiting"
                st.session_state.msg_index = random.randint(0, len(WAITING_MESSAGES)-1)
                st.session_state.step_index = 0
                st.rerun()
            else:
                st.error("Please enter a question.")

    # Check existing question
    st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("Check my question →", use_container_width=True):
            st.session_state.show_check = not st.session_state.show_check
            st.rerun()

    if st.session_state.show_check:
        st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            check_id = st.text_input("", placeholder="Enter your question ID (e.g. A3F2B1C9)",
                                     label_visibility="collapsed").strip().upper()
            if check_id:
                q = get_question(check_id)
                if q is None:
                    st.error("Question not found. It may have expired.")
                elif q["status"] == "answered":
                    st.session_state.question_id = q["id"]
                    st.session_state.question_text = q["question"]
                    st.session_state.answer = q["answer"]
                    st.session_state.page = "answered"
                    st.rerun()
                else:
                    st.session_state.question_id = q["id"]
                    st.session_state.question_text = q["question"]
                    st.session_state.page = "waiting"
                    st.session_state.msg_index = random.randint(0, len(WAITING_MESSAGES)-1)
                    st.session_state.step_index = 0
                    st.rerun()

    # Hidden admin dot
    st.markdown("<div style='height:4rem;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([3,1,3])
    with col2:
        if st.button("·", use_container_width=True, key="admin_toggle"):
            st.session_state.show_admin_input = not st.session_state.show_admin_input
            st.rerun()

    if st.session_state.show_admin_input:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            pw = st.text_input("", type="password", placeholder="Access code",
                               label_visibility="collapsed", key="admin_pw")
            if pw == ADMIN_KEY:
                st.session_state.page = "admin_verified"
                st.rerun()
            elif pw:
                st.error("Incorrect.")

# ── WAITING PAGE ──────────────────────────────────────────────────────────────
elif st.session_state.page == "waiting":
    msg = WAITING_MESSAGES[st.session_state.msg_index % len(WAITING_MESSAGES)]
    step = FAKE_STEPS[st.session_state.step_index % len(FAKE_STEPS)]
    emoji, headline, subline = msg

    st.markdown(f"""
    <div style='text-align:center;padding:2.5rem 0 1.5rem;animation:fadein 0.3s ease;'>
        <div style='font-size:3.5rem;margin-bottom:1rem;animation:float 2.5s ease-in-out infinite;display:inline-block;'>{emoji}</div>
        <div style='font-size:1.25rem;font-weight:600;color:#ececec;margin-bottom:0.3rem;'>{headline}</div>
        <div style='color:#555;font-size:0.9em;'>{subline}</div>
    </div>
    """, unsafe_allow_html=True)

    q_text = st.session_state.question_text
    qid = st.session_state.question_id
    st.markdown(f"""
    <div style='background:#161616;border:1px solid #222;border-radius:10px;padding:1rem 1.2rem;margin:0 0 1rem;'>
        <div style='font-size:0.7em;color:#444;margin-bottom:0.4rem;text-transform:uppercase;letter-spacing:0.05em;'>Your question</div>
        <div style='color:#ccc;font-size:0.95em;'>"{q_text}"</div>
    </div>
    """, unsafe_allow_html=True)

    # Question ID — prominent, copyable
    st.markdown(f"""
    <div style='background:#0a0a0a;border:1px solid #1e1e1e;border-radius:8px;padding:0.8rem 1.2rem;margin:0 0 1.2rem;text-align:center;'>
        <div style='font-size:0.7em;color:#444;margin-bottom:0.3rem;text-transform:uppercase;letter-spacing:0.05em;'>Your question ID — save this to check back later</div>
        <div style='font-size:1.5rem;font-weight:700;color:#ff4500;letter-spacing:0.15em;font-family:monospace;'>{qid}</div>
        <div style='font-size:0.7em;color:#333;margin-top:0.3rem;'>You can close this tab and return anytime</div>
    </div>
    """, unsafe_allow_html=True)

    # Fake progress
    st.markdown("""
    <div style='margin-bottom:1rem;'>
        <div style='background:#161616;border-radius:4px;height:3px;overflow:hidden;'>
            <div style='height:100%;width:97%;background:linear-gradient(90deg,#ff4500,#ff8c00);animation:progress-stuck 4s ease-out forwards;'></div>
        </div>
        <div style='text-align:right;font-size:0.68em;color:#333;margin-top:0.3rem;'>97%</div>
    </div>
    """, unsafe_allow_html=True)

    completed = "".join(
        f'<div style="color:#2a4a2a;font-size:0.72em;">✓ {FAKE_STEPS[i]}</div>'
        for i in range(min(st.session_state.step_index, 7))
    )
    st.markdown(f"""
    <div style='background:#0a0a0a;border:1px solid #1a1a1a;border-radius:8px;padding:0.8rem 1rem;margin-bottom:1.5rem;font-family:monospace;'>
        {completed}
        <div style='color:#ff4500;font-size:0.72em;'>
            <span style='animation:blink 0.9s infinite;display:inline-block;'>▌</span> {step}
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2,1,2])
    with col2:
        if st.button("← Back", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

    # Poll for answer
    time.sleep(5)
    q = get_question(st.session_state.question_id)
    if q and q["status"] == "answered":
        st.session_state.answer = q["answer"]
        st.session_state.page = "answered"
        st.rerun()
    else:
        st.session_state.msg_index = (st.session_state.msg_index + 1) % len(WAITING_MESSAGES)
        st.session_state.step_index = min(st.session_state.step_index + 1, len(FAKE_STEPS) - 1)
        st.rerun()

# ── ANSWERED PAGE ─────────────────────────────────────────────────────────────
elif st.session_state.page == "answered":
    st.markdown("""
    <div style='text-align:center;padding:2rem 0 1.5rem;animation:fadein 0.4s ease;'>
        <div style='font-size:2.5rem;margin-bottom:0.8rem;'>🤖</div>
        <div style='font-size:1.3rem;font-weight:600;color:#ececec;'>MrGPT responded.</div>
    </div>
    """, unsafe_allow_html=True)

    q_text = st.session_state.question_text
    st.markdown(f"""
    <div style='background:#111;border-radius:10px;padding:0.8rem 1.2rem;margin:0 0 0.8rem;border-left:2px solid #333;'>
        <div style='font-size:0.7em;color:#444;margin-bottom:0.3rem;text-transform:uppercase;letter-spacing:0.05em;'>You asked</div>
        <div style='color:#888;font-size:0.9em;'>"{q_text}"</div>
    </div>
    """, unsafe_allow_html=True)

    answer_text = st.session_state.answer or ""
    st.markdown(f"""
    <div style='
        background:#161616;border:1px solid #2a2a2a;border-left:2px solid #ff4500;
        border-radius:10px;padding:1.4rem;margin:0 0 1.5rem;animation:fadein 0.5s ease;
    '>
        <div style='font-size:0.7em;color:#ff4500;margin-bottom:0.7rem;text-transform:uppercase;letter-spacing:0.05em;'>MrGPT</div>
        <div style='color:#ececec;font-size:1em;line-height:1.7;'>{answer_text}</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("Ask another question", use_container_width=True):
            st.session_state.page = "home"
            st.session_state.question_id = None
            st.session_state.question_text = ""
            st.session_state.answer = None
            st.session_state.step_index = 0
            st.rerun()

    st.markdown("""
    <div style='text-align:center;margin-top:3rem;color:#222;font-size:0.72em;'>MrGPT · AI Assistant</div>
    """, unsafe_allow_html=True)
