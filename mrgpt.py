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
    "Finalizing neural output...",
    "97% complete...",
    "97% complete...",
    "97% complete...",
    "Still 97%... this is normal...",
    "97% complete (we promise)...",
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
@import url('https://fonts.googleapis.com/css2?family=Söhne:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    background-color: #212121;
    color: #ececec;
    font-family: 'Inter', ui-sans-serif, system-ui, sans-serif;
    margin: 0;
    padding: 0;
}

.block-container {
    max-width: 760px;
    padding: 0 1rem;
    margin: 0 auto;
}

#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebar"] { display: none; }

/* Buttons */
.stButton > button {
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
}
.stButton > button:hover {
    background: #3a3a3a;
    border-color: #555;
}

/* Textarea - ChatGPT style */
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
    min-height: 56px;
}
.stTextArea textarea:focus {
    border-color: #686868;
    box-shadow: none;
    outline: none;
}
.stTextArea textarea::placeholder { color: #6b6b6b; }

/* Text input */
.stTextInput input {
    background: #2f2f2f;
    border: 1px solid #424242;
    border-radius: 8px;
    color: #ececec;
    font-family: 'Inter', sans-serif;
    font-size: 0.95em;
    padding: 0.6em 1em;
}
.stTextInput input:focus {
    border-color: #686868;
    box-shadow: none;
    outline: none;
}
.stTextInput input::placeholder { color: #6b6b6b; }

/* Containers */
[data-testid="stContainer"] {
    background: #2f2f2f;
    border: 1px solid #424242;
    border-radius: 12px;
}

/* Remove extra padding streamlit adds */
.stMarkdown p { margin: 0; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #212121; }
::-webkit-scrollbar-thumb { background: #424242; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #555; }

/* Animations */
@keyframes float {
    0%,100% { transform: translateY(0); }
    50% { transform: translateY(-5px); }
}
@keyframes blink {
    0%,100% { opacity: 1; }
    50% { opacity: 0; }
}
@keyframes fadein {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes progress-stuck {
    0% { width: 0%; }
    50% { width: 97%; }
    100% { width: 97%; }
}
@keyframes typein {
    from { opacity: 0; }
    to { opacity: 1; }
}
@keyframes pulse {
    0%,100% { opacity: 0.4; }
    50% { opacity: 1; }
}
</style>
""", unsafe_allow_html=True)

for k, v in [("page","home"), ("question_id",None), ("question_text",""),
             ("answer",None), ("msg_index",0), ("step_index",0),
             ("show_admin_input",False)]:
    if k not in st.session_state:
        st.session_state[k] = v

params = st.query_params
is_admin = params.get("admin","") == ADMIN_KEY

# ── ADMIN PAGE ────────────────────────────────────────────────────────────────
if is_admin or st.session_state.page == "admin_verified":
    st.markdown("""
    <div style='padding:2rem 0 1.5rem;border-bottom:1px solid #333;margin-bottom:1.5rem;'>
        <div style='font-size:0.75em;color:#6b6b6b;margin-bottom:0.2rem;font-family:monospace;'>STAFF · MrGPT</div>
        <div style='font-size:1.5em;font-weight:600;color:#ececec;'>Inbox</div>
    </div>
    """, unsafe_allow_html=True)

    data = get_data()
    pending = [q for q in data["questions"] if q["status"] == "pending"]
    answered = [q for q in data["questions"] if q["status"] == "answered"]

    if not pending:
        st.markdown("""
        <div style='text-align:center;padding:5rem 0;color:#6b6b6b;'>
            <div style='font-size:2rem;margin-bottom:0.8rem;'>✓</div>
            <div style='font-size:0.95em;'>All caught up.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='color:#ff6b35;font-size:0.82em;font-weight:500;margin-bottom:1.2rem;letter-spacing:0.03em;'>{len(pending)} PENDING</div>", unsafe_allow_html=True)
        for q in pending:
            with st.container(border=True):
                asked_time = q["asked_at"][:16].replace("T"," at ")
                st.markdown(f"""
                <div style='font-size:0.68em;color:#6b6b6b;margin-bottom:0.6rem;font-family:monospace;'>{asked_time} · #{q['id']}</div>
                <div style='font-size:1em;color:#ececec;margin-bottom:1rem;line-height:1.5;font-weight:500;'>"{q['question']}"</div>
                """, unsafe_allow_html=True)
                answer = st.text_area("", key=f"ans_{q['id']}", height=80,
                                      placeholder="Reply as MrGPT...", label_visibility="collapsed")
                c1, c2 = st.columns([5,1])
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
        st.markdown("<div style='margin-top:2rem;'></div>", unsafe_allow_html=True)
        with st.expander(f"History — {len(answered)} answered"):
            for q in reversed(answered):
                st.markdown(f"""
                <div style='margin-bottom:1rem;padding:0.9rem;background:#1a1a1a;border-radius:8px;'>
                    <div style='color:#6b6b6b;font-size:0.82em;margin-bottom:0.4rem;'>Q: {q['question']}</div>
                    <div style='color:#ececec;font-size:0.88em;line-height:1.5;'>A: {q['answer']}</div>
                </div>
                """, unsafe_allow_html=True)
    st.stop()

# ── HOME PAGE ─────────────────────────────────────────────────────────────────
if st.session_state.page == "home":
    # Big centered logo area — ChatGPT style
    st.markdown("""
    <div style='text-align:center;padding:5rem 0 2rem;animation:fadein 0.4s ease;'>
        <div style='
            width:52px;height:52px;
            background:linear-gradient(135deg,#ff6b35,#ff4500);
            border-radius:14px;
            display:inline-flex;align-items:center;justify-content:center;
            font-size:1.6rem;
            margin-bottom:1.2rem;
            animation:float 3s ease-in-out infinite;
            box-shadow:0 8px 24px rgba(255,107,53,0.25);
        '>🤖</div>
        <h1 style='
            font-size:2rem;
            font-weight:700;
            color:#ececec;
            margin:0 0 0.5rem;
            letter-spacing:-0.02em;
        '>What can I help with?</h1>
        <p style='color:#6b6b6b;font-size:0.9em;margin:0;'>Powered by MrGPT™ Neural Engine</p>
    </div>
    """, unsafe_allow_html=True)

    question = st.text_area("", placeholder="Message MrGPT...",
                             height=100, label_visibility="collapsed")

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("↑  Send message", use_container_width=True):
            if question.strip():
                qid = submit_question(question.strip())
                st.session_state.question_id = qid
                st.session_state.question_text = question.strip()
                st.session_state.page = "waiting"
                st.session_state.msg_index = random.randint(0, len(WAITING_MESSAGES)-1)
                st.session_state.step_index = 0
                st.rerun()
            else:
                st.warning("Type something first.")

    # Suggestion chips — ChatGPT style
    st.markdown("""
    <div style='display:flex;flex-wrap:wrap;gap:0.5rem;justify-content:center;margin-top:1.5rem;'>
        <div style='background:#2f2f2f;border:1px solid #424242;border-radius:20px;padding:0.4rem 1rem;font-size:0.82em;color:#ababab;'>✨ Explain something</div>
        <div style='background:#2f2f2f;border:1px solid #424242;border-radius:20px;padding:0.4rem 1rem;font-size:0.82em;color:#ababab;'>💡 Give me ideas</div>
        <div style='background:#2f2f2f;border:1px solid #424242;border-radius:20px;padding:0.4rem 1rem;font-size:0.82em;color:#ababab;'>🤔 Ask me anything</div>
        <div style='background:#2f2f2f;border:1px solid #424242;border-radius:20px;padding:0.4rem 1rem;font-size:0.82em;color:#ababab;'>🎯 Help me decide</div>
    </div>
    """, unsafe_allow_html=True)

    # Footer with hidden admin
    st.markdown("<div style='height:5rem;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align:center;color:#3a3a3a;font-size:0.72em;'>
        MrGPT can make mistakes. Consider checking important info.
    </div>
    """, unsafe_allow_html=True)

    # Hidden admin — disguised as "Terms" in footer
    col1, col2, col3, col4, col5 = st.columns([2,1,1,1,2])
    with col2:
        st.markdown("<div style='text-align:center;color:#2a2a2a;font-size:0.68em;margin-top:0.3rem;'>Privacy</div>", unsafe_allow_html=True)
    with col3:
        if st.button("Terms", key="admin_toggle"):
            st.session_state.show_admin_input = not st.session_state.show_admin_input
            st.rerun()
        st.markdown("<style>div[data-testid='column']:nth-child(3) .stButton>button{background:transparent;border:none;color:#2a2a2a;font-size:0.68em;padding:0;min-height:0;width:auto;}</style>", unsafe_allow_html=True)
    with col4:
        st.markdown("<div style='text-align:center;color:#2a2a2a;font-size:0.68em;margin-top:0.3rem;'>About</div>", unsafe_allow_html=True)

    if st.session_state.show_admin_input:
        col1, col2, col3 = st.columns([2,1,2])
        with col2:
            pw = st.text_input("", type="password", placeholder="••••••••",
                               label_visibility="collapsed", key="admin_pw")
            if pw == ADMIN_KEY:
                st.session_state.page = "admin_verified"
                st.rerun()
            elif pw:
                st.error("Incorrect.")

# ── WAITING PAGE ──────────────────────────────────────────────────────────────
elif st.session_state.page == "waiting":
    q_text = st.session_state.question_text
    msg = WAITING_MESSAGES[st.session_state.msg_index % len(WAITING_MESSAGES)]
    step = FAKE_STEPS[st.session_state.step_index % len(FAKE_STEPS)]
    emoji, headline, subline = msg

    # User message bubble — ChatGPT style
    st.markdown(f"""
    <div style='
        display:flex;justify-content:flex-end;
        margin:2rem 0 1.5rem;
        animation:fadein 0.3s ease;
    '>
        <div style='
            background:#2f2f2f;
            border-radius:18px 18px 4px 18px;
            padding:0.9rem 1.2rem;
            max-width:80%;
            color:#ececec;
            font-size:0.95em;
            line-height:1.6;
            border:1px solid #424242;
        '>{q_text}</div>
    </div>
    """, unsafe_allow_html=True)

    # MrGPT response area — typing indicator style
    st.markdown(f"""
    <div style='
        display:flex;align-items:flex-start;gap:0.8rem;
        margin-bottom:1.5rem;
        animation:fadein 0.4s ease 0.2s both;
    '>
        <div style='
            width:34px;height:34px;min-width:34px;
            background:linear-gradient(135deg,#ff6b35,#ff4500);
            border-radius:8px;
            display:flex;align-items:center;justify-content:center;
            font-size:1rem;
            box-shadow:0 2px 8px rgba(255,107,53,0.3);
            margin-top:2px;
        '>🤖</div>
        <div style='flex:1;'>
            <div style='font-size:0.82em;font-weight:600;color:#ababab;margin-bottom:0.5rem;'>MrGPT</div>
            <div style='
                background:#2f2f2f;
                border:1px solid #424242;
                border-radius:4px 18px 18px 18px;
                padding:1rem 1.2rem;
            '>
                <div style='font-size:1.5rem;margin-bottom:0.5rem;animation:float 2s ease-in-out infinite;display:inline-block;'>{emoji}</div>
                <div style='font-size:0.95em;font-weight:600;color:#ececec;margin-bottom:0.2rem;'>{headline}</div>
                <div style='font-size:0.85em;color:#6b6b6b;margin-bottom:1rem;'>{subline}</div>

                <div style='margin-bottom:0.8rem;'>
                    <div style='background:#1a1a1a;border-radius:4px;height:3px;overflow:hidden;'>
                        <div style='height:100%;width:97%;background:linear-gradient(90deg,#ff6b35,#ff8c00);animation:progress-stuck 5s ease-out forwards;'></div>
                    </div>
                    <div style='display:flex;justify-content:space-between;font-size:0.65em;color:#3a3a3a;margin-top:0.2rem;'>
                        <span>Processing...</span><span>97%</span>
                    </div>
                </div>

                <div style='font-family:monospace;font-size:0.7em;color:#4a4a4a;'>
                    <span style='animation:blink 1s infinite;display:inline-block;color:#ff6b35;'>▌</span> {step}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Typing dots row
    st.markdown("""
    <div style='display:flex;align-items:center;gap:0.4rem;padding:0 0 1.5rem 3rem;'>
        <div style='width:6px;height:6px;background:#555;border-radius:50%;animation:pulse 1.2s ease-in-out infinite;'></div>
        <div style='width:6px;height:6px;background:#555;border-radius:50%;animation:pulse 1.2s ease-in-out 0.2s infinite;'></div>
        <div style='width:6px;height:6px;background:#555;border-radius:50%;animation:pulse 1.2s ease-in-out 0.4s infinite;'></div>
        <span style='font-size:0.72em;color:#555;margin-left:0.4rem;'>MrGPT is thinking...</span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2,1,2])
    with col2:
        if st.button("← New chat", use_container_width=True):
            st.session_state.page = "home"
            st.session_state.question_id = None
            st.rerun()

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
    q_text = st.session_state.question_text
    answer_text = st.session_state.answer or ""

    # User bubble
    st.markdown(f"""
    <div style='
        display:flex;justify-content:flex-end;
        margin:2rem 0 1.5rem;
        animation:fadein 0.3s ease;
    '>
        <div style='
            background:#2f2f2f;
            border-radius:18px 18px 4px 18px;
            padding:0.9rem 1.2rem;
            max-width:80%;
            color:#ececec;
            font-size:0.95em;
            line-height:1.6;
            border:1px solid #424242;
        '>{q_text}</div>
    </div>
    """, unsafe_allow_html=True)

    # MrGPT response bubble
    st.markdown(f"""
    <div style='
        display:flex;align-items:flex-start;gap:0.8rem;
        margin-bottom:2rem;
        animation:fadein 0.5s ease 0.1s both;
    '>
        <div style='
            width:34px;height:34px;min-width:34px;
            background:linear-gradient(135deg,#ff6b35,#ff4500);
            border-radius:8px;
            display:flex;align-items:center;justify-content:center;
            font-size:1rem;
            box-shadow:0 2px 8px rgba(255,107,53,0.3);
            margin-top:2px;
        '>🤖</div>
        <div style='flex:1;'>
            <div style='font-size:0.82em;font-weight:600;color:#ababab;margin-bottom:0.5rem;'>MrGPT</div>
            <div style='
                color:#ececec;
                font-size:0.97em;
                line-height:1.75;
                padding:0.2rem 0;
            '>{answer_text}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='border-top:1px solid #2f2f2f;margin-bottom:1.5rem;'></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("↑  Ask another question", use_container_width=True):
            st.session_state.page = "home"
            st.session_state.question_id = None
            st.session_state.question_text = ""
            st.session_state.answer = None
            st.session_state.step_index = 0
            st.rerun()

    st.markdown("""
    <div style='text-align:center;color:#3a3a3a;font-size:0.72em;margin-top:2rem;'>
        MrGPT can make mistakes. Consider checking important info.
    </div>
    """, unsafe_allow_html=True)
