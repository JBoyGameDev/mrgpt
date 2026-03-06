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
MAX_CONVOS      = 10
MAX_MESSAGES    = 5

MODEL_NAMES = [
    "MrGPT-9 Turbo Ultra Pro Max",
    "MrGPT Haiku (Bad at Poetry Edition)",
    "MrGPT Sonnet (Never Read One)",
    "MrGPT Opus (No Idea What That Means)",
    "MrGPT-o1 (The o Stands for Oops)",
    "MrGPT Flash (Deceptively Slow)",
    "MrGPT Extended Thinking (Takes Naps)",
    "MrGPT Vision (Legally Blind)",
    "MrGPT Instruct (Does Not Follow Instructions)",
    "MrGPT Nano (Still Huge)",
]

PERSONAS = {
    "default":  {"name": "MrGPT",       "title": "General AI Assistant",        "desc": "Ask me anything."},
    "coach":    {"name": "Coach GPT",    "title": "Life Coach & Motivational AI", "desc": "Ready to unlock your potential."},
    "chef":     {"name": "Chef GPT",     "title": "Culinary Intelligence System", "desc": "Ask me about food or recipes."},
    "advisor":  {"name": "Finance GPT",  "title": "AI Financial Advisor",         "desc": "Your money, my algorithms."},
}

WAITING_MESSAGES = [
    ("MrGPT is playing Minecraft right now.", "He will answer you between rounds."),
    ("MrGPT is asleep.", "His dedication to your question is truly inspiring."),
    ("MrGPT is eating.", "Do not disturb. Seriously."),
    ("MrGPT has seen your message.", "He left it on read. Intentionally."),
    ("MrGPT stepped outside for some air.", "In January. Without a jacket."),
    ("MrGPT is watching YouTube.", "For research purposes."),
    ("MrGPT is arguing with someone online.", "Your question is next. Probably."),
    ("MrGPT is in the bathroom.", "This could take anywhere from 2 to 45 minutes."),
    ("MrGPT is making a playlist.", "Very relevant to your question, trust."),
    ("Consulting the ancient texts.", "It is Reddit."),
    ("MrGPT battery at 2 percent.", "Peak performance mode activated."),
    ("MrGPT is mentally on vacation.", "Physically at his desk. Spiritually gone."),
    ("BEEP BOOP PROCESSING.", "This is definitely a real AI and not a person."),
    ("You are number 1 in queue.", "Queue currently has 847 other questions."),
    ("MrGPT has entered sleep mode.", "Expected wake time: unknown."),
    ("MrGPT is thinking really hard.", "Or he forgot. Hard to tell."),
    ("Running at 12 percent capacity.", "This IS peak performance."),
    ("MrGPT rolled a die to decide.", "He got a 3. Whatever that means."),
    ("Neural pathways activating.", "Nothing is happening. We are working on it."),
    ("Transmitting across the servers.", "The servers are a guy named Dave."),
    ("MrGPT is getting coffee.", "Fourth cup today. He is fine."),
    ("Answers at the speed of thought.", "MrGPT thinks quite slowly."),
    ("Cross-referencing 47 billion data points.", "The data points are vibes."),
    ("MrGPT is pondering your question.", "He finds it deeply confusing."),
    ("Loading.", "Has been loading since 2019."),
    ("MrGPT is feeding ducks.", "This is somehow relevant to your query."),
    ("Processing power at historic lows.", "Please hold."),
    ("MrGPT is in his feelings right now.", "Your question hit different."),
    ("MrGPT is at the gym.", "He will not be taking questions at this time."),
    ("Quantum inference in progress.", "The quantum is not cooperating."),
]

def get_data():
    try:
        r = requests.get(f"{JSONBIN_URL}/latest", headers=HEADERS, timeout=8)
        record = r.json().get("record", {})
        if "conversations" not in record:
            record["conversations"] = {}
        return record
    except:
        return {"conversations": {}}

def save_data(data):
    try:
        requests.put(JSONBIN_URL, headers=HEADERS, json=data, timeout=8)
    except:
        pass

def new_debate(topic, position_a, label_a):
    data = get_data()
    if "debates" not in data:
        data["debates"] = {}
    did = str(uuid.uuid4())[:8].upper()
    data["debates"][did] = {
        "id": did,
        "topic": topic,
        "side_a": {"position": position_a, "label": label_a},
        "side_b": None,
        "verdict": None,
        "winner": None,
        "status": "waiting_b",
        "votes": {"a": 0, "b": 0},
        "created_at": datetime.now().isoformat(),
    }
    save_data(data)
    return did

def join_debate(did, position_b, label_b):
    data = get_data()
    if "debates" not in data or did not in data["debates"]:
        return False
    data["debates"][did]["side_b"] = {"position": position_b, "label": label_b}
    data["debates"][did]["status"] = "pending"
    save_data(data)
    return True

def get_debate(did):
    data = get_data()
    return data.get("debates", {}).get(did)

def answer_debate(did, verdict, winner):
    data = get_data()
    if "debates" not in data or did not in data["debates"]:
        return
    data["debates"][did]["verdict"] = verdict
    data["debates"][did]["winner"] = winner
    data["debates"][did]["status"] = "answered"
    save_data(data)

def vote_debate(did, side):
    data = get_data()
    if "debates" not in data or did not in data["debates"]:
        return
    data["debates"][did]["votes"][side] = data["debates"][did]["votes"].get(side, 0) + 1
    save_data(data)

def new_roast(name, age, job, fact, wildcard):
    data = get_data()
    if "roasts" not in data:
        data["roasts"] = {}
    rid = str(uuid.uuid4())[:8].upper()
    data["roasts"][rid] = {
        "id": rid,
        "name": name, "age": age, "job": job,
        "fact": fact, "wildcard": wildcard,
        "roast": None, "status": "pending",
        "created_at": datetime.now().isoformat(),
    }
    save_data(data)
    return rid

def get_roast(rid):
    data = get_data()
    return data.get("roasts", {}).get(rid)

def answer_roast(rid, roast_text):
    data = get_data()
    if "roasts" not in data or rid not in data["roasts"]:
        return
    data["roasts"][rid]["roast"] = roast_text
    data["roasts"][rid]["status"] = "answered"
    save_data(data)

def new_conversation(persona_key):
    data = get_data()
    cid = str(uuid.uuid4())[:8].upper()
    data["conversations"][cid] = {
        "id": cid, "persona": persona_key, "messages": [],
        "revealed": False, "created_at": datetime.now().isoformat(),
    }
    convos = data["conversations"]
    if len(convos) > MAX_CONVOS:
        sorted_keys = sorted(convos.keys(), key=lambda k: convos[k].get("created_at", ""))
        for old_key in sorted_keys[:len(convos) - MAX_CONVOS]:
            del convos[old_key]
    save_data(data)
    return cid

def add_message(cid, question_text):
    data = get_data()
    if cid not in data["conversations"]:
        return None
    mid = str(uuid.uuid4())[:6].upper()
    data["conversations"][cid]["messages"].append({
        "id": mid, "question": question_text, "answer": None,
        "status": "pending", "rating": None,
        "asked_at": datetime.now().isoformat(),
    })
    save_data(data)
    return mid

def get_conversation(cid):
    data = get_data()
    return data["conversations"].get(cid)

def answer_message(cid, mid, answer_text):
    data = get_data()
    if cid not in data["conversations"]:
        return
    for m in data["conversations"][cid]["messages"]:
        if m["id"] == mid:
            m["answer"] = answer_text
            m["status"] = "answered"
            m["answered_at"] = datetime.now().isoformat()
            break
    save_data(data)

def rate_message(cid, mid, rating):
    data = get_data()
    if cid not in data["conversations"]:
        return
    for m in data["conversations"][cid]["messages"]:
        if m["id"] == mid:
            m["rating"] = rating
            break
    save_data(data)

def reveal_conversation(cid):
    data = get_data()
    if cid not in data["conversations"]:
        return
    data["conversations"][cid]["revealed"] = True
    data["conversations"][cid]["messages"].append({
        "id": "REVEAL", "question": None,
        "answer": "By the way — I am not actually an AI. I am a real person who has been answering your questions this whole time. Hope that was fun.",
        "status": "answered", "rating": None,
        "asked_at": datetime.now().isoformat(),
        "answered_at": datetime.now().isoformat(),
        "is_reveal": True,
    })
    save_data(data)

def delete_conversation(cid):
    data = get_data()
    if cid in data["conversations"]:
        del data["conversations"][cid]
    save_data(data)

st.set_page_config(page_title="MrGPT", page_icon="M", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Styrene+A:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300;1,9..40,400&family=DM+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    background-color: #1a1916;
    color: #d4d0c8;
    font-family: 'DM Sans', ui-sans-serif, system-ui, sans-serif;
}

.block-container {
    max-width: 680px !important;
    padding: 0 1.5rem !important;
    margin: 0 auto;
}

#MainMenu, footer { visibility: hidden; }
header { background: transparent !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #141410 !important;
    border-right: 1px solid #242420;
}
[data-testid="stSidebar"] .block-container {
    padding: 1rem 0.75rem !important;
    max-width: 100% !important;
}
[data-testid="stSidebarContent"] { padding: 0 !important; }

[data-testid="stSidebar"] .stButton > button {
    background: transparent;
    color: #5a5850;
    border: none;
    border-radius: 6px;
    font-size: 0.82em;
    font-weight: 400;
    padding: 0.45rem 0.7rem;
    text-align: left;
    width: 100%;
    transition: all 0.1s;
    font-family: 'DM Sans', sans-serif;
    letter-spacing: 0.01em;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #1e1e1a;
    color: #d4d0c8;
}

/* selectbox in sidebar */
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: #1e1e1a !important;
    border: 1px solid #2a2a24 !important;
    border-radius: 6px !important;
    color: #5a5850 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72em !important;
}
[data-testid="stSidebar"] .stSelectbox label { display: none; }

/* Main buttons */
section.main .stButton > button {
    background: #242420;
    color: #d4d0c8;
    border: 1px solid #2e2e28;
    border-radius: 8px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    font-size: 0.88em;
    letter-spacing: 0.01em;
    padding: 0.6em 1.2em;
    transition: all 0.12s;
    width: 100%;
}
section.main .stButton > button:hover {
    background: #2a2a24;
    border-color: #3a3a32;
}

/* Send button — accent */
.send-btn .stButton > button {
    background: #c9642a;
    border-color: #c9642a;
    color: #fff;
    font-weight: 600;
}
.send-btn .stButton > button:hover {
    background: #b85c26;
    border-color: #b85c26;
}

/* Textarea */
.stTextArea textarea {
    background: #1e1e1a;
    border: 1px solid #2e2e28;
    border-radius: 12px;
    color: #d4d0c8;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.96em;
    line-height: 1.7;
    padding: 0.9rem 1.1rem;
    resize: none;
    transition: border-color 0.12s;
}
.stTextArea textarea:focus {
    border-color: #5a5248;
    box-shadow: none;
    outline: none;
}
.stTextArea textarea::placeholder { color: #3a3830; }

.stTextInput input {
    background: #1e1e1a !important;
    border: 1px solid #2e2e28 !important;
    border-radius: 8px !important;
    color: #d4d0c8 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9em !important;
}
.stTextInput input:focus {
    border-color: #5a5248 !important;
    box-shadow: none !important;
}
.stTextInput input::placeholder { color: #3a3830 !important; }

[data-testid="stContainer"] {
    background: #1e1e1a;
    border: 1px solid #2a2a24;
    border-radius: 10px;
}
[data-testid="stExpander"] {
    background: #161612;
    border: 1px solid #242420;
    border-radius: 8px;
}

hr { border-color: #242420 !important; }

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #141410; }
::-webkit-scrollbar-thumb { background: #2a2a24; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #3a3830; }

/* ── Logo mark ── */
.mrgpt-logo {
    width: 28px; height: 28px;
    background: linear-gradient(135deg, #c9642a, #e8a060, #c9642a);
    background-size: 200%;
    border-radius: 6px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 0.85rem;
    color: #fff;
    letter-spacing: -0.02em;
    font-family: 'DM Sans', sans-serif;
    flex-shrink: 0;
}

/* ── Message styling — no bubbles, just text ── */
.msg-you {
    padding: 1.4rem 0 0.4rem;
    border-top: 1px solid #242420;
    margin-top: 0.5rem;
}
.msg-you-label {
    font-size: 0.72em;
    font-weight: 600;
    color: #3a3830;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-family: 'DM Mono', monospace;
    margin-bottom: 0.5rem;
}
.msg-you-text {
    font-size: 0.97em;
    color: #d4d0c8;
    line-height: 1.7;
    font-family: 'DM Sans', sans-serif;
}
.msg-ai {
    padding: 0.6rem 0 1.2rem;
}
.msg-ai-label {
    font-size: 0.72em;
    font-weight: 600;
    color: #c9642a;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-family: 'DM Mono', monospace;
    margin-bottom: 0.6rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}
.msg-ai-text {
    font-size: 0.97em;
    color: #d4d0c8;
    line-height: 1.85;
    font-family: 'DM Sans', sans-serif;
}

/* ── Animations ── */
@keyframes fadein { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
@keyframes blink { 0%,100% { opacity: 1; } 50% { opacity: 0; } }
@keyframes pulse-dot { 0%,100% { opacity: 0.2; transform: scale(0.75); } 50% { opacity: 0.7; transform: scale(1); } }
@keyframes progress-stuck { 0% { width: 0%; } 55% { width: 94%; } 70% { width: 97%; } 100% { width: 97%; } }
@keyframes shimmer-logo {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in [
    ("page", "home"), ("conv_id", None), ("persona", "default"),
    ("show_admin_input", False), ("chat_history", []),
    ("pending_mid", None), ("msg_index", 0),
    ("selected_model", MODEL_NAMES[0]),
    ("debate_id", None), ("roast_id", None),
]:
    if k not in st.session_state:
        st.session_state[k] = v

params = st.query_params
is_admin = params.get("admin", "") == ADMIN_KEY

url_conv = params.get("id", "")
if url_conv and not st.session_state.conv_id:
    st.session_state.conv_id = url_conv.upper()
    st.session_state.page = "chat"

if params.get("leak", "") == "true":
    st.session_state.page = "leak"

url_debate = params.get("debate", "")
if url_debate and not st.session_state.debate_id:
    st.session_state.debate_id = url_debate.upper()
    st.session_state.page = "debate_join"

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
<div style='padding:0.6rem 0.2rem 1rem;display:flex;align-items:center;gap:0.6rem;'>
    <div style='width:28px;height:28px;background:linear-gradient(135deg,#c9642a,#e8a060,#c9642a);background-size:200%;border-radius:6px;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:0.82rem;color:#fff;font-family:DM Sans,sans-serif;flex-shrink:0;animation:shimmer-logo 4s ease-in-out infinite;'>M</div>
    <span style='font-weight:600;font-size:0.95em;color:#d4d0c8;font-family:DM Sans,sans-serif;letter-spacing:-0.01em;'>MrGPT</span>
</div>
""", unsafe_allow_html=True)

    chosen_model = st.selectbox(
        "", MODEL_NAMES,
        index=MODEL_NAMES.index(st.session_state.selected_model),
        key="model_select", label_visibility="collapsed"
    )
    if chosen_model != st.session_state.selected_model:
        st.session_state.selected_model = chosen_model
        st.rerun()

    st.markdown("<div style='height:0.6rem;'></div>", unsafe_allow_html=True)

    if st.button("New conversation", key="sb_new", use_container_width=True):
        st.session_state.page = "home"
        st.session_state.conv_id = None
        st.session_state.pending_mid = None
        st.rerun()

    if st.button("About MrGPT", key="sb_about", use_container_width=True):
        st.session_state.page = "about"
        st.rerun()

    if st.button("Debates", key="sb_debates", use_container_width=True):
        st.session_state.page = "debates_home"
        st.rerun()

    if st.button("Roast Me", key="sb_roast", use_container_width=True):
        st.session_state.page = "roast_home"
        st.rerun()

    st.markdown("<div style='height:0.3rem;'></div><hr style='border-color:#1e1e1a;margin:0.4rem 0;'>", unsafe_allow_html=True)

    if st.session_state.chat_history:
        st.markdown("<div style='font-size:0.62em;color:#2e2e28;padding:0.4rem 0.4rem 0.5rem;text-transform:uppercase;letter-spacing:0.1em;font-family:DM Mono,monospace;'>Recents</div>", unsafe_allow_html=True)
        for i, chat in enumerate(reversed(st.session_state.chat_history[-10:])):
            label = chat["question"][:30] + ("..." if len(chat["question"]) > 30 else "")
            if st.button(label, key=f"hist_{i}", use_container_width=True):
                st.session_state.conv_id = chat["conv_id"]
                st.session_state.page = "chat"
                st.rerun()
    else:
        st.markdown("<div style='font-size:0.75em;color:#242420;padding:0.5rem;text-align:center;font-family:DM Mono,monospace;'>No conversations yet</div>", unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#1e1e1a;margin:0.4rem 0;'>", unsafe_allow_html=True)

    if st.button("Settings", key="sb_admin_toggle", use_container_width=True):
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
            st.markdown("<div style='font-size:0.72em;color:#a04040;padding:0.2rem 0.5rem;'>Incorrect.</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ADMIN
# ══════════════════════════════════════════════════════════════════════════════
if is_admin or st.session_state.page == "admin_verified":
    st.markdown("<div style='height:2rem;'></div>", unsafe_allow_html=True)
    col_back, col_title, col_refresh = st.columns([1, 3, 1])
    with col_back:
        if st.button("Back", key="admin_back", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
    with col_title:
        st.markdown("<div style='text-align:center;padding:0.2rem 0 1rem;'><div style='font-size:0.68em;color:#3a3830;font-family:DM Mono,monospace;letter-spacing:0.1em;'>STAFF ACCESS</div><div style='font-size:1.4em;font-weight:600;color:#d4d0c8;letter-spacing:-0.02em;'>Inbox</div></div>", unsafe_allow_html=True)
    with col_refresh:
        if st.button("Refresh", key="admin_refresh", use_container_width=True):
            st.rerun()

    data = get_data()
    convos = data.get("conversations", {})
    active = [(cid, c) for cid, c in convos.items()
              if any(m["status"] == "pending" for m in c["messages"])]
    closed = [(cid, c) for cid, c in convos.items()
              if not any(m["status"] == "pending" for m in c["messages"]) and c["messages"]]

    if not active:
        st.markdown("<div style='text-align:center;padding:4rem 0;color:#2e2e28;font-family:DM Mono,monospace;font-size:0.85em;'>Nothing pending.</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='color:#c9642a;font-size:0.72em;font-weight:600;margin-bottom:1rem;letter-spacing:0.08em;font-family:DM Mono,monospace;'>{len(active)} ACTIVE</div>", unsafe_allow_html=True)
        for cid, convo in active:
            p = PERSONAS.get(convo.get("persona", "default"), PERSONAS["default"])
            with st.container(border=True):
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    st.markdown(f"<div style='font-size:0.65em;color:#3a3830;font-family:DM Mono,monospace;margin-bottom:0.4rem;'>{p['name']} / #{cid}</div>", unsafe_allow_html=True)
                with col_b:
                    if not convo.get("revealed"):
                        if st.button("Reveal", key=f"reveal_{cid}", use_container_width=True):
                            reveal_conversation(cid)
                            st.rerun()

                for m in convo["messages"]:
                    if m.get("is_reveal"):
                        continue
                    r = m.get("rating", "")
                    rstr = " [+]" if r == "up" else (" [-]" if r == "down" else "")
                    if m["status"] == "answered":
                        st.markdown(f"<div style='padding:0.5rem 0;border-bottom:1px solid #242420;'><div style='font-size:0.78em;color:#3a3830;'>Q: {m['question']}</div><div style='font-size:0.82em;color:#d4d0c8;margin-top:0.2rem;'>A: {m['answer']}{rstr}</div></div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div style='padding:0.6rem 0;border-left:2px solid #c9642a;padding-left:0.8rem;margin:0.5rem 0;'><div style='font-size:0.68em;color:#c9642a;font-family:DM Mono,monospace;margin-bottom:0.3rem;'>PENDING / {m['id']}</div><div style='font-size:1em;color:#d4d0c8;font-weight:500;'>{m['question']}</div></div>", unsafe_allow_html=True)
                        ans = st.text_area("", key=f"ans_{cid}_{m['id']}", height=70,
                                           placeholder="Reply...", label_visibility="collapsed")
                        c1, c2 = st.columns([5, 1])
                        with c1:
                            if st.button("Send", key=f"sub_{cid}_{m['id']}", use_container_width=True):
                                if ans.strip():
                                    answer_message(cid, m["id"], ans.strip())
                                    st.rerun()
                        with c2:
                            if st.button("Delete", key=f"del_{cid}", use_container_width=True):
                                delete_conversation(cid)
                                st.rerun()

    if closed:
        st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)
        with st.expander(f"History ({len(closed)})"):
            for cid, convo in reversed(closed[-5:]):
                p = PERSONAS.get(convo.get("persona", "default"), PERSONAS["default"])
                st.markdown(f"<div style='font-size:0.65em;color:#3a3830;font-family:DM Mono,monospace;margin-bottom:0.4rem;'>{p['name']} / #{cid}</div>", unsafe_allow_html=True)
                for m in convo["messages"]:
                    if m.get("answer") and m.get("question"):
                        r = " [+]" if m.get("rating") == "up" else (" [-]" if m.get("rating") == "down" else "")
                        st.markdown(f"<div style='font-size:0.8em;padding:0.4rem 0;border-bottom:1px solid #242420;'><div style='color:#3a3830;'>Q: {m['question']}</div><div style='color:#d4d0c8;'>A: {m['answer']}{r}</div></div>", unsafe_allow_html=True)
                st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

    # ── ADMIN: DEBATES ────────────────────────────────────────────────────────
    data2 = get_data()
    pending_debates = [(did, d) for did, d in data2.get("debates", {}).items() if d["status"] == "pending"]
    if pending_debates:
        st.markdown("<hr style='border-color:#242420;margin:2rem 0 1.5rem;'>", unsafe_allow_html=True)
        st.markdown(f"<div style='color:#c9642a;font-size:0.72em;font-weight:600;margin-bottom:1rem;letter-spacing:0.08em;font-family:DM Mono,monospace;'>DEBATES — {len(pending_debates)} PENDING</div>", unsafe_allow_html=True)
        for did, debate in pending_debates:
            with st.container(border=True):
                st.markdown(f"<div style='font-size:0.65em;color:#3a3830;font-family:DM Mono,monospace;margin-bottom:0.6rem;'>#{did}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-size:1em;font-weight:600;color:#d4d0c8;margin-bottom:1rem;'>Topic: {debate['topic']}</div>", unsafe_allow_html=True)
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"<div style='background:#1e1e1a;border:1px solid #2e2e28;border-radius:8px;padding:0.8rem;'><div style='font-size:0.65em;color:#3a3830;font-family:DM Mono,monospace;margin-bottom:0.3rem;'>SIDE A — {debate['side_a']['label']}</div><div style='font-size:0.85em;color:#d4d0c8;line-height:1.6;'>{debate['side_a']['position']}</div></div>", unsafe_allow_html=True)
                with col_b:
                    st.markdown(f"<div style='background:#1e1e1a;border:1px solid #2e2e28;border-radius:8px;padding:0.8rem;'><div style='font-size:0.65em;color:#3a3830;font-family:DM Mono,monospace;margin-bottom:0.3rem;'>SIDE B — {debate['side_b']['label']}</div><div style='font-size:0.85em;color:#d4d0c8;line-height:1.6;'>{debate['side_b']['position']}</div></div>", unsafe_allow_html=True)
                verdict = st.text_area("", key=f"dverdict_{did}", height=80, placeholder="Write MrGPT's verdict...", label_visibility="collapsed")
                winner = st.radio("Winner:", ["Side A", "Side B", "Both wrong, frankly"], key=f"dwinner_{did}", horizontal=True)
                if st.button("Deliver verdict", key=f"dsub_{did}", use_container_width=True):
                    if verdict.strip():
                        w = "a" if "A" in winner else ("b" if "B" in winner else "neither")
                        answer_debate(did, verdict.strip(), w)
                        st.rerun()

    # ── ADMIN: ROASTS ─────────────────────────────────────────────────────────
    data3 = get_data()
    pending_roasts = [(rid, r) for rid, r in data3.get("roasts", {}).items() if r["status"] == "pending"]
    if pending_roasts:
        st.markdown("<hr style='border-color:#242420;margin:2rem 0 1.5rem;'>", unsafe_allow_html=True)
        st.markdown(f"<div style='color:#c9642a;font-size:0.72em;font-weight:600;margin-bottom:1rem;letter-spacing:0.08em;font-family:DM Mono,monospace;'>ROASTS — {len(pending_roasts)} PENDING</div>", unsafe_allow_html=True)
        for rid, roast in pending_roasts:
            with st.container(border=True):
                st.markdown(f"<div style='font-size:0.65em;color:#3a3830;font-family:DM Mono,monospace;margin-bottom:0.5rem;'>#{rid}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='padding:0.8rem;background:#1e1e1a;border-radius:8px;margin-bottom:0.8rem;'><div style='font-size:0.72em;color:#3a3830;font-family:DM Mono,monospace;margin-bottom:0.4rem;'>PROFILE</div><div style='font-size:0.85em;color:#d4d0c8;line-height:1.8;'>Name: {roast['name']}<br>Age: {roast['age']}<br>Job: {roast['job']}<br>Embarrassing fact: {roast['fact']}<br>Wildcard: {roast.get('wildcard') or 'none'}</div></div>", unsafe_allow_html=True)
                roast_text = st.text_area("", key=f"roasttxt_{rid}", height=100, placeholder="Write the roast...", label_visibility="collapsed")
                if st.button("Deliver roast", key=f"roastsub_{rid}", use_container_width=True):
                    if roast_text.strip():
                        answer_roast(rid, roast_text.strip())
                        st.rerun()

    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# ABOUT
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "about":
    st.markdown("""
<div style='padding:4rem 0 2.5rem;animation:fadein 0.4s ease;'>
    <div style='font-size:0.72em;color:#3a3830;font-family:DM Mono,monospace;letter-spacing:0.1em;margin-bottom:0.8rem;'>ABOUT</div>
    <h1 style='font-size:2.4rem;font-weight:700;color:#d4d0c8;margin:0 0 1.2rem;letter-spacing:-0.03em;line-height:1.1;'>MrGPT is not like other AI companies.</h1>
    <p style='color:#5a5850;font-size:1em;line-height:1.8;margin-bottom:1.5rem;'>MrGPT was founded in a garage in 2019 by a team of world-class researchers, engineers, and one guy who really just wanted to see what would happen. After years of rigorous training, unsafe testing, and a brief but memorable partnership with a fortune cookie manufacturer in Guangzhou, MrGPT-1 was born. It did not work at all.</p>
    <p style='color:#5a5850;font-size:1em;line-height:1.8;margin-bottom:1.5rem;'>By MrGPT-4, the team had pivoted from "general intelligence" to "plausible confidence," which proved far more achievable and, frankly, more useful. Users reported feeling satisfied with responses 94% of the time. The remaining 6% reported confusion, which the team classified as "expected behavior."</p>
    <p style='color:#5a5850;font-size:1em;line-height:1.8;margin-bottom:2.5rem;'>MrGPT-9, the current model, represents the culmination of everything the team has learned. It is fast, mostly coherent, and has never once caught fire. The team considers this their greatest achievement.</p>
    <hr style='border-color:#242420;margin-bottom:2.5rem;'>
    <div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:1.5rem;margin-bottom:2.5rem;'>
        <div>
            <div style='font-size:2rem;font-weight:700;color:#c9642a;font-family:DM Sans,sans-serif;letter-spacing:-0.03em;'>1.8M</div>
            <div style='font-size:0.78em;color:#3a3830;margin-top:0.2rem;'>Questions answered</div>
            <div style='font-size:0.6em;color:#242420;font-family:DM Mono,monospace;margin-top:0.1rem;'>number unverified</div>
        </div>
        <div>
            <div style='font-size:2rem;font-weight:700;color:#c9642a;font-family:DM Sans,sans-serif;letter-spacing:-0.03em;'>99.7%</div>
            <div style='font-size:0.78em;color:#3a3830;margin-top:0.2rem;'>Accuracy rate</div>
            <div style='font-size:0.6em;color:#242420;font-family:DM Mono,monospace;margin-top:0.1rem;'>not measured</div>
        </div>
        <div>
            <div style='font-size:2rem;font-weight:700;color:#c9642a;font-family:DM Sans,sans-serif;letter-spacing:-0.03em;'>0</div>
            <div style='font-size:0.78em;color:#3a3830;margin-top:0.2rem;'>Fires caused</div>
            <div style='font-size:0.6em;color:#242420;font-family:DM Mono,monospace;margin-top:0.1rem;'>as of last quarter</div>
        </div>
    </div>
    <div style='background:#1e1e1a;border:1px solid #242420;border-radius:10px;padding:1.5rem;margin-bottom:1.5rem;'>
        <div style='font-size:0.68em;font-weight:600;color:#3a3830;margin-bottom:0.8rem;text-transform:uppercase;letter-spacing:0.1em;font-family:DM Mono,monospace;'>Safety</div>
        <p style='color:#5a5850;font-size:0.9em;line-height:1.75;margin:0;'>MrGPT is committed to the responsible development of artificial intelligence, or whatever this is. Our safety team reviews all outputs on a rolling basis, which in practice means Dave checks the logs when he remembers. We take misuse seriously and have a strict policy against it, though we acknowledge that policy has never been tested.</p>
    </div>
    <div style='background:#1e1e1a;border:1px solid #242420;border-radius:10px;padding:1.5rem;'>
        <div style='font-size:0.68em;font-weight:600;color:#3a3830;margin-bottom:0.8rem;text-transform:uppercase;letter-spacing:0.1em;font-family:DM Mono,monospace;'>Legal</div>
        <p style='color:#3a3830;font-size:0.8em;line-height:1.7;margin:0;font-family:DM Mono,monospace;'>MrGPT Industries LLC is not responsible for decisions made based on MrGPT responses, consequences thereof, financial losses, relationship damage, failed exam answers, bad recipe outcomes, or any general confusion. MrGPT is not a doctor, lawyer, financial advisor, chef, or life coach, even when operating in those modes. Use of this service constitutes agreement to terms that do not exist.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HOME
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "home":
    st.markdown("""
<div style='padding:5rem 0 2.5rem;animation:fadein 0.35s ease;'>
    <div style='display:flex;align-items:center;gap:0.7rem;margin-bottom:2rem;'>
        <div style='width:36px;height:36px;background:linear-gradient(135deg,#c9642a,#e8a060,#c9642a);background-size:200%;border-radius:9px;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:1rem;color:#fff;font-family:DM Sans,sans-serif;animation:shimmer-logo 4s ease-in-out infinite;'>M</div>
        <span style='font-size:1.6rem;font-weight:700;color:#d4d0c8;letter-spacing:-0.03em;'>Good to see you.</span>
    </div>
    <p style='color:#3a3830;font-size:0.88em;font-family:DM Mono,monospace;margin:0 0 2rem;'>MrGPT is ready. Probably.</p>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div style='font-size:0.75em;color:#3a3830;font-weight:500;margin-bottom:0.6rem;font-family:DM Mono,monospace;letter-spacing:0.04em;'>SELECT PERSONA</div>", unsafe_allow_html=True)
    cols = st.columns(4)
    for i, (pkey, pdata) in enumerate(PERSONAS.items()):
        with cols[i]:
            selected = st.session_state.persona == pkey
            border = "#c9642a" if selected else "#242420"
            bg = "#1e1e1a" if selected else "#161612"
            label_color = "#c9642a" if selected else "#3a3830"
            st.markdown(f"<div style='background:{bg};border:1px solid {border};border-radius:8px;padding:0.7rem 0.6rem;text-align:center;margin-bottom:0.3rem;'><div style='font-size:0.8em;font-weight:600;color:{label_color};font-family:DM Sans,sans-serif;'>{pdata['name']}</div><div style='font-size:0.62em;color:#2e2e28;margin-top:0.2rem;font-family:DM Mono,monospace;'>{pdata['title']}</div></div>", unsafe_allow_html=True)
            if st.button("Select" if not selected else "Selected", key=f"p_{pkey}", use_container_width=True):
                st.session_state.persona = pkey
                st.rerun()

    st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)

    question = st.text_area("", placeholder="What do you want to know?", height=110, label_visibility="collapsed")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Send", use_container_width=True, key="home_send"):
            if question.strip():
                cid = new_conversation(st.session_state.persona)
                mid = add_message(cid, question.strip())
                st.session_state.conv_id = cid
                st.session_state.pending_mid = mid
                st.session_state.msg_index = random.randint(0, len(WAITING_MESSAGES) - 1)
                st.session_state.page = "chat"
                st.session_state.chat_history.append({"question": question.strip(), "conv_id": cid})
                st.rerun()
            else:
                st.warning("Type something first.")

    st.markdown("<div style='text-align:center;margin-top:3.5rem;color:#242420;font-size:0.68em;font-family:DM Mono,monospace;'>MrGPT can make mistakes. Consider checking important info.</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CHAT
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "chat":
    cid = st.session_state.conv_id
    if not cid:
        st.session_state.page = "home"
        st.rerun()

    convo = get_conversation(cid)
    if not convo:
        st.session_state.page = "home"
        st.rerun()

    persona = PERSONAS.get(convo.get("persona", "default"), PERSONAS["default"])
    messages = convo.get("messages", [])
    pending = [m for m in messages if m["status"] == "pending"]

    # Share ID bar
    st.markdown(f"<div style='padding:1.2rem 0 0.3rem;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #242420;margin-bottom:0.5rem;'><div style='font-size:0.72em;color:#2e2e28;font-family:DM Mono,monospace;'>{persona['name']} / {persona['title']}</div><div style='font-size:0.68em;color:#2e2e28;font-family:DM Mono,monospace;'>ID: {cid}</div></div>", unsafe_allow_html=True)

    for m in messages:
        if m.get("is_reveal"):
            st.markdown(f"<div style='border-left:2px solid #c9642a;padding:0.8rem 1rem;margin:1.2rem 0;animation:fadein 0.4s ease;'><div style='font-size:0.65em;color:#c9642a;font-family:DM Mono,monospace;letter-spacing:0.08em;margin-bottom:0.4rem;'>SYSTEM</div><div style='color:#d4d0c8;font-size:0.94em;line-height:1.7;font-family:DM Sans,sans-serif;'>{m['answer']}</div></div>", unsafe_allow_html=True)
            continue

        # User message
        if m.get("question"):
            st.markdown(f"<div class='msg-you' style='animation:fadein 0.3s ease;'><div class='msg-you-label'>You</div><div class='msg-you-text'>{m['question']}</div></div>", unsafe_allow_html=True)

        # AI answered
        if m["status"] == "answered" and m.get("answer"):
            st.markdown(f"<div class='msg-ai' style='animation:fadein 0.4s ease;'><div class='msg-ai-label'><div style='width:18px;height:18px;background:linear-gradient(135deg,#c9642a,#e8a060);border-radius:4px;display:inline-flex;align-items:center;justify-content:center;font-weight:800;font-size:0.6rem;color:#fff;'> M</div>{persona['name']}</div><div class='msg-ai-text'>{m['answer']}</div></div>", unsafe_allow_html=True)

            # Ratings
            if m.get("rating") is None and m["id"] != "REVEAL":
                rc1, rc2, rc3 = st.columns([1, 1, 8])
                with rc1:
                    if st.button("+", key=f"up_{m['id']}"):
                        rate_message(cid, m["id"], "up")
                        st.rerun()
                with rc2:
                    if st.button("-", key=f"dn_{m['id']}"):
                        rate_message(cid, m["id"], "down")
                        st.rerun()
            elif m.get("rating"):
                sign = "[+]" if m["rating"] == "up" else "[-]"
                st.markdown(f"<div style='font-size:0.7em;color:#2e2e28;padding:0 0 0.5rem;font-family:DM Mono,monospace;'>{sign}</div>", unsafe_allow_html=True)

        # Pending — waiting screen, plain text only
        elif m["status"] == "pending":
            headline, subline = WAITING_MESSAGES[st.session_state.msg_index % len(WAITING_MESSAGES)]
            st.markdown(f"""
<div class='msg-ai' style='animation:fadein 0.4s ease;'>
    <div class='msg-ai-label'>
        <div style='width:18px;height:18px;background:linear-gradient(135deg,#c9642a,#e8a060);border-radius:4px;display:inline-flex;align-items:center;justify-content:center;font-weight:800;font-size:0.6rem;color:#fff;'>M</div>
        {persona['name']}
    </div>
    <div style='padding:1.2rem 0;'>
        <div style='font-size:1.05rem;font-weight:500;color:#d4d0c8;margin-bottom:0.3rem;line-height:1.5;font-family:DM Sans,sans-serif;'>{headline}</div>
        <div style='font-size:0.85em;color:#3a3830;margin-bottom:1.2rem;font-family:DM Sans,sans-serif;'>{subline}</div>
        <div style='background:#242420;border-radius:100px;height:2px;overflow:hidden;max-width:160px;'>
            <div style='height:100%;background:linear-gradient(90deg,#c9642a,#e8a060);animation:progress-stuck 10s ease-out forwards;'></div>
        </div>
    </div>
</div>
<div style='display:flex;align-items:center;gap:4px;padding:0 0 0.8rem;'>
    <div style='width:5px;height:5px;background:#2e2e28;border-radius:50%;animation:pulse-dot 1.2s ease-in-out infinite;'></div>
    <div style='width:5px;height:5px;background:#2e2e28;border-radius:50%;animation:pulse-dot 1.2s ease-in-out 0.2s infinite;'></div>
    <div style='width:5px;height:5px;background:#2e2e28;border-radius:50%;animation:pulse-dot 1.2s ease-in-out 0.4s infinite;'></div>
</div>
""", unsafe_allow_html=True)
            time.sleep(5)
            fresh = get_conversation(cid)
            fresh_msg = next((x for x in fresh["messages"] if x["id"] == m["id"]), None)
            if fresh_msg and fresh_msg["status"] == "answered":
                st.session_state.msg_index = random.randint(0, len(WAITING_MESSAGES) - 1)
                st.rerun()
            else:
                st.session_state.msg_index = (st.session_state.msg_index + 1) % len(WAITING_MESSAGES)
                st.rerun()

    # Follow-up input
    if not pending and not convo.get("revealed"):
        msg_count = len([m for m in messages if not m.get("is_reveal")])
        st.markdown("<div style='border-top:1px solid #242420;margin-top:0.5rem;padding-top:1.2rem;'></div>", unsafe_allow_html=True)
        if msg_count < MAX_MESSAGES:
            st.markdown(f"<div style='font-size:0.65em;color:#2a2a24;font-family:DM Mono,monospace;text-align:right;margin-bottom:0.4rem;'>{msg_count} / {MAX_MESSAGES}</div>", unsafe_allow_html=True)
            followup = st.text_area("", placeholder="Ask a follow-up...", height=80, label_visibility="collapsed", key="followup")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("Send", use_container_width=True, key="send_followup"):
                    if followup.strip():
                        mid = add_message(cid, followup.strip())
                        st.session_state.msg_index = random.randint(0, len(WAITING_MESSAGES) - 1)
                        st.session_state.chat_history.append({"question": followup.strip(), "conv_id": cid})
                        st.rerun()
        else:
            st.markdown("<div style='text-align:center;padding:1rem;color:#2e2e28;font-size:0.8em;font-family:DM Mono,monospace;'>Conversation limit reached.</div>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("New conversation", use_container_width=True):
                    st.session_state.page = "home"
                    st.session_state.conv_id = None
                    st.rerun()

    st.markdown("<div style='text-align:center;color:#1e1e1a;font-size:0.65em;margin-top:2.5rem;font-family:DM Mono,monospace;'>MrGPT can make mistakes. Consider checking important info.</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DEBATES HOME
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "debates_home":
    st.markdown("""
<div style='padding:4rem 0 2rem;animation:fadein 0.35s ease;'>
    <div style='font-size:0.68em;color:#3a3830;font-family:DM Mono,monospace;letter-spacing:0.1em;margin-bottom:0.6rem;'>DEBATES</div>
    <h1 style='font-size:2rem;font-weight:700;color:#d4d0c8;margin:0 0 0.6rem;letter-spacing:-0.03em;'>Let MrGPT settle it.</h1>
    <p style='color:#3a3830;font-size:0.88em;line-height:1.7;margin:0 0 2.5rem;font-family:DM Mono,monospace;'>Two positions. One verdict. Zero accountability.</p>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div style='font-size:0.72em;color:#3a3830;font-family:DM Mono,monospace;letter-spacing:0.06em;margin-bottom:0.5rem;'>THE TOPIC</div>", unsafe_allow_html=True)
    topic = st.text_input("", placeholder="e.g. Is a hot dog a sandwich?", label_visibility="collapsed", key="debate_topic")

    st.markdown("<div style='font-size:0.72em;color:#3a3830;font-family:DM Mono,monospace;letter-spacing:0.06em;margin:1rem 0 0.5rem;'>YOUR NAME OR HANDLE</div>", unsafe_allow_html=True)
    label_a = st.text_input("", placeholder="e.g. Jake", label_visibility="collapsed", key="debate_label_a")

    st.markdown("<div style='font-size:0.72em;color:#3a3830;font-family:DM Mono,monospace;letter-spacing:0.06em;margin:1rem 0 0.5rem;'>YOUR POSITION</div>", unsafe_allow_html=True)
    pos_a = st.text_area("", placeholder="State your case. Be compelling. MrGPT is watching.", height=100, label_visibility="collapsed", key="debate_pos_a")

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("Start debate", use_container_width=True, key="debate_start"):
            if topic.strip() and pos_a.strip() and label_a.strip():
                did = new_debate(topic.strip(), pos_a.strip(), label_a.strip())
                st.session_state.debate_id = did
                st.session_state.page = "debate_waiting_b"
                st.rerun()
            else:
                st.warning("Fill in all fields.")

    st.markdown("<div style='margin-top:2rem;padding:1rem;background:#1e1e1a;border:1px solid #242420;border-radius:8px;'><div style='font-size:0.68em;color:#3a3830;font-family:DM Mono,monospace;margin-bottom:0.4rem;'>HOW IT WORKS</div><div style='font-size:0.82em;color:#3a3830;line-height:1.7;font-family:DM Sans,sans-serif;'>You submit a topic and your position. You get a link to send your opponent. They submit their side. MrGPT deliberates and delivers a verdict. Both of you see the result. MrGPT is always right.</div></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DEBATE WAITING FOR OPPONENT
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "debate_waiting_b":
    did = st.session_state.debate_id
    debate = get_debate(did)
    if not debate:
        st.session_state.page = "debates_home"
        st.rerun()

    base_url = "https://mrgpt-ai.streamlit.app"
    share_url = f"{base_url}?debate={did}"

    st.markdown(f"""
<div style='padding:4rem 0 2rem;animation:fadein 0.35s ease;'>
    <div style='font-size:0.68em;color:#3a3830;font-family:DM Mono,monospace;letter-spacing:0.1em;margin-bottom:0.6rem;'>DEBATES / #{did}</div>
    <h1 style='font-size:1.8rem;font-weight:700;color:#d4d0c8;margin:0 0 0.4rem;letter-spacing:-0.03em;'>Waiting for your opponent.</h1>
    <p style='color:#3a3830;font-size:0.85em;font-family:DM Mono,monospace;margin:0 0 2rem;'>Send them the link below. Once they submit, MrGPT deliberates.</p>
    <div style='background:#1e1e1a;border:1px solid #2e2e28;border-radius:8px;padding:1rem 1.2rem;margin-bottom:2rem;'>
        <div style='font-size:0.65em;color:#3a3830;font-family:DM Mono,monospace;margin-bottom:0.4rem;'>SHARE THIS LINK WITH YOUR OPPONENT</div>
        <div style='font-size:0.85em;color:#c9642a;font-family:DM Mono,monospace;word-break:break-all;'>{share_url}</div>
    </div>
    <div style='border-left:2px solid #2e2e28;padding-left:1rem;margin-bottom:2rem;'>
        <div style='font-size:0.65em;color:#3a3830;font-family:DM Mono,monospace;margin-bottom:0.3rem;'>TOPIC</div>
        <div style='font-size:1em;color:#d4d0c8;font-weight:600;'>{debate['topic']}</div>
    </div>
    <div style='background:#1e1e1a;border:1px solid #242420;border-radius:8px;padding:0.9rem 1rem;'>
        <div style='font-size:0.65em;color:#3a3830;font-family:DM Mono,monospace;margin-bottom:0.3rem;'>YOUR POSITION — {debate['side_a']['label']}</div>
        <div style='font-size:0.88em;color:#5a5850;line-height:1.6;'>{debate['side_a']['position']}</div>
    </div>
</div>
""", unsafe_allow_html=True)

    time.sleep(5)
    fresh = get_debate(did)
    if fresh and fresh["status"] in ("pending", "answered"):
        st.session_state.page = "debate_view"
        st.rerun()
    else:
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# DEBATE JOIN (opponent side)
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "debate_join":
    did = st.session_state.debate_id
    debate = get_debate(did)
    if not debate:
        st.warning("Debate not found.")
        st.session_state.page = "debates_home"
        st.rerun()

    if debate["side_b"] is not None:
        st.session_state.page = "debate_view"
        st.rerun()

    st.markdown(f"""
<div style='padding:4rem 0 2rem;animation:fadein 0.35s ease;'>
    <div style='font-size:0.68em;color:#3a3830;font-family:DM Mono,monospace;letter-spacing:0.1em;margin-bottom:0.6rem;'>DEBATES / #{did}</div>
    <h1 style='font-size:1.8rem;font-weight:700;color:#d4d0c8;margin:0 0 0.4rem;letter-spacing:-0.03em;'>You have been challenged.</h1>
    <p style='color:#3a3830;font-size:0.85em;font-family:DM Mono,monospace;margin:0 0 2rem;'>Submit your side. MrGPT will decide who is right.</p>
    <div style='border-left:2px solid #c9642a;padding-left:1rem;margin-bottom:2rem;'>
        <div style='font-size:0.65em;color:#3a3830;font-family:DM Mono,monospace;margin-bottom:0.3rem;'>TOPIC</div>
        <div style='font-size:1.1em;color:#d4d0c8;font-weight:600;'>{debate['topic']}</div>
    </div>
    <div style='background:#1e1e1a;border:1px solid #242420;border-radius:8px;padding:0.9rem 1rem;margin-bottom:1.5rem;'>
        <div style='font-size:0.65em;color:#3a3830;font-family:DM Mono,monospace;margin-bottom:0.3rem;'>THEIR POSITION — {debate['side_a']['label']}</div>
        <div style='font-size:0.88em;color:#5a5850;line-height:1.6;'>{debate['side_a']['position']}</div>
    </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div style='font-size:0.72em;color:#3a3830;font-family:DM Mono,monospace;letter-spacing:0.06em;margin-bottom:0.5rem;'>YOUR NAME OR HANDLE</div>", unsafe_allow_html=True)
    label_b = st.text_input("", placeholder="e.g. Alex", label_visibility="collapsed", key="debate_label_b")

    st.markdown("<div style='font-size:0.72em;color:#3a3830;font-family:DM Mono,monospace;letter-spacing:0.06em;margin:1rem 0 0.5rem;'>YOUR POSITION</div>", unsafe_allow_html=True)
    pos_b = st.text_area("", placeholder="Make your case. Be ruthless.", height=100, label_visibility="collapsed", key="debate_pos_b")

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("Submit my side", use_container_width=True, key="debate_join_submit"):
            if pos_b.strip() and label_b.strip():
                join_debate(did, pos_b.strip(), label_b.strip())
                st.session_state.page = "debate_view"
                st.rerun()
            else:
                st.warning("Fill in all fields.")

# ══════════════════════════════════════════════════════════════════════════════
# DEBATE VIEW (waiting for verdict / showing verdict)
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "debate_view":
    did = st.session_state.debate_id
    debate = get_debate(did)
    if not debate:
        st.session_state.page = "debates_home"
        st.rerun()

    st.markdown(f"""
<div style='padding:2.5rem 0 1.5rem;'>
    <div style='font-size:0.68em;color:#3a3830;font-family:DM Mono,monospace;letter-spacing:0.1em;margin-bottom:0.5rem;'>DEBATES / #{did}</div>
    <h2 style='font-size:1.6rem;font-weight:700;color:#d4d0c8;margin:0 0 0.3rem;letter-spacing:-0.02em;'>{debate['topic']}</h2>
    <div style='font-size:0.72em;color:#3a3830;font-family:DM Mono,monospace;'>MrGPT is considering both sides carefully.</div>
</div>
""", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"<div style='background:#1e1e1a;border:1px solid #2e2e28;border-radius:8px;padding:1rem;height:100%;'><div style='font-size:0.65em;color:#3a3830;font-family:DM Mono,monospace;margin-bottom:0.4rem;'>SIDE A — {debate['side_a']['label']}</div><div style='font-size:0.88em;color:#d4d0c8;line-height:1.65;'>{debate['side_a']['position']}</div></div>", unsafe_allow_html=True)
    with col_b:
        side_b = debate.get("side_b")
        if side_b:
            st.markdown(f"<div style='background:#1e1e1a;border:1px solid #2e2e28;border-radius:8px;padding:1rem;height:100%;'><div style='font-size:0.65em;color:#3a3830;font-family:DM Mono,monospace;margin-bottom:0.4rem;'>SIDE B — {side_b['label']}</div><div style='font-size:0.88em;color:#d4d0c8;line-height:1.65;'>{side_b['position']}</div></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background:#161612;border:1px dashed #242420;border-radius:8px;padding:1rem;text-align:center;color:#2e2e28;font-size:0.82em;font-family:DM Mono,monospace;'>Waiting for opponent...</div>", unsafe_allow_html=True)

    if debate["status"] == "answered" and debate.get("verdict"):
        winner = debate.get("winner", "neither")
        winner_label = debate["side_a"]["label"] if winner == "a" else (debate["side_b"]["label"] if winner == "b" else "Nobody")
        st.markdown(f"""
<div style='margin:2rem 0;padding:1.5rem;background:#1e1e1a;border:1px solid #2e2e28;border-top:2px solid #c9642a;border-radius:8px;animation:fadein 0.5s ease;'>
    <div style='font-size:0.65em;color:#c9642a;font-family:DM Mono,monospace;letter-spacing:0.1em;margin-bottom:0.3rem;'>MRGPT VERDICT</div>
    <div style='font-size:0.68em;color:#3a3830;font-family:DM Mono,monospace;margin-bottom:1rem;'>Winner: {winner_label}</div>
    <div style='font-size:0.97em;color:#d4d0c8;line-height:1.8;font-family:DM Sans,sans-serif;'>{debate['verdict']}</div>
</div>
""", unsafe_allow_html=True)

        # Voting
        votes = debate.get("votes", {"a": 0, "b": 0})
        total = (votes.get("a", 0) + votes.get("b", 0)) or 1
        st.markdown(f"<div style='font-size:0.7em;color:#3a3830;font-family:DM Mono,monospace;margin-bottom:0.5rem;'>Do you agree with MrGPT?</div>", unsafe_allow_html=True)
        vc1, vc2, vc3 = st.columns([1,1,3])
        with vc1:
            if st.button(f"Yes ({votes.get('a',0)})", key="vote_agree", use_container_width=True):
                vote_debate(did, "a")
                st.rerun()
        with vc2:
            if st.button(f"No ({votes.get('b',0)})", key="vote_disagree", use_container_width=True):
                vote_debate(did, "b")
                st.rerun()
    else:
        headline, subline = WAITING_MESSAGES[st.session_state.msg_index % len(WAITING_MESSAGES)]
        st.markdown(f"""
<div style='margin:2rem 0;border-left:2px solid #2e2e28;padding-left:1rem;'>
    <div style='font-size:0.65em;color:#3a3830;font-family:DM Mono,monospace;letter-spacing:0.1em;margin-bottom:0.5rem;'>MRGPT IS DELIBERATING</div>
    <div style='font-size:1rem;font-weight:500;color:#d4d0c8;margin-bottom:0.2rem;'>{headline}</div>
    <div style='font-size:0.82em;color:#3a3830;'>{subline}</div>
    <div style='margin-top:1rem;background:#242420;border-radius:100px;height:2px;overflow:hidden;max-width:120px;'>
        <div style='height:100%;background:linear-gradient(90deg,#c9642a,#e8a060);animation:progress-stuck 10s ease-out forwards;'></div>
    </div>
</div>
""", unsafe_allow_html=True)
        time.sleep(5)
        st.session_state.msg_index = (st.session_state.msg_index + 1) % len(WAITING_MESSAGES)
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# ROAST HOME
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "roast_home":
    st.markdown("""
<div style='padding:4rem 0 2rem;animation:fadein 0.35s ease;'>
    <div style='font-size:0.68em;color:#3a3830;font-family:DM Mono,monospace;letter-spacing:0.1em;margin-bottom:0.6rem;'>ROAST ME</div>
    <h1 style='font-size:2rem;font-weight:700;color:#d4d0c8;margin:0 0 0.5rem;letter-spacing:-0.03em;'>Submit yourself to MrGPT.</h1>
    <p style='color:#3a3830;font-size:0.85em;font-family:DM Mono,monospace;margin:0 0 2rem;'>MrGPT will roast you. You asked for this. This is your fault.</p>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div style='font-size:0.72em;color:#3a3830;font-family:DM Mono,monospace;letter-spacing:0.06em;margin-bottom:0.5rem;'>YOUR NAME</div>", unsafe_allow_html=True)
    r_name = st.text_input("", placeholder="What should MrGPT call you?", label_visibility="collapsed", key="r_name")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div style='font-size:0.72em;color:#3a3830;font-family:DM Mono,monospace;letter-spacing:0.06em;margin:1rem 0 0.5rem;'>AGE</div>", unsafe_allow_html=True)
        r_age = st.text_input("", placeholder="How old?", label_visibility="collapsed", key="r_age")
    with col2:
        st.markdown("<div style='font-size:0.72em;color:#3a3830;font-family:DM Mono,monospace;letter-spacing:0.06em;margin:1rem 0 0.5rem;'>JOB</div>", unsafe_allow_html=True)
        r_job = st.text_input("", placeholder="What do you do?", label_visibility="collapsed", key="r_job")

    st.markdown("<div style='font-size:0.72em;color:#3a3830;font-family:DM Mono,monospace;letter-spacing:0.06em;margin:1rem 0 0.5rem;'>ONE EMBARRASSING FACT ABOUT YOURSELF</div>", unsafe_allow_html=True)
    r_fact = st.text_area("", placeholder="The more specific, the better. MrGPT feeds on this.", height=80, label_visibility="collapsed", key="r_fact")

    st.markdown("<div style='font-size:0.72em;color:#3a3830;font-family:DM Mono,monospace;letter-spacing:0.06em;margin:1rem 0 0.5rem;'>ANYTHING ELSE MRGPT SHOULD KNOW (optional)</div>", unsafe_allow_html=True)
    r_wild = st.text_area("", placeholder="Give MrGPT more ammunition.", height=60, label_visibility="collapsed", key="r_wild")

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("Roast me", use_container_width=True, key="roast_submit"):
            if r_name.strip() and r_fact.strip() and r_job.strip():
                rid = new_roast(r_name.strip(), r_age.strip(), r_job.strip(), r_fact.strip(), r_wild.strip())
                st.session_state.roast_id = rid
                st.session_state.page = "roast_waiting"
                st.rerun()
            else:
                st.warning("Name, job, and embarrassing fact are required.")

# ══════════════════════════════════════════════════════════════════════════════
# ROAST WAITING
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "roast_waiting":
    rid = st.session_state.roast_id
    roast = get_roast(rid)
    if not roast:
        st.session_state.page = "roast_home"
        st.rerun()

    headline, subline = WAITING_MESSAGES[st.session_state.msg_index % len(WAITING_MESSAGES)]

    st.markdown(f"""
<div style='padding:4rem 0 2rem;animation:fadein 0.4s ease;'>
    <div style='font-size:0.68em;color:#3a3830;font-family:DM Mono,monospace;letter-spacing:0.1em;margin-bottom:0.6rem;'>ROAST ME / #{rid}</div>
    <h2 style='font-size:1.6rem;font-weight:700;color:#d4d0c8;margin:0 0 0.3rem;letter-spacing:-0.02em;'>MrGPT is preparing your roast.</h2>
    <p style='color:#3a3830;font-size:0.82em;font-family:DM Mono,monospace;margin:0 0 2.5rem;'>This may take a moment. MrGPT wants to get it right.</p>
    <div style='border-left:2px solid #2e2e28;padding-left:1rem;margin-bottom:2rem;'>
        <div style='font-size:0.95em;font-weight:500;color:#d4d0c8;margin-bottom:0.2rem;'>{headline}</div>
        <div style='font-size:0.82em;color:#3a3830;'>{subline}</div>
    </div>
    <div style='background:#242420;border-radius:100px;height:2px;overflow:hidden;max-width:140px;margin-bottom:2.5rem;'>
        <div style='height:100%;background:linear-gradient(90deg,#c9642a,#e8a060);animation:progress-stuck 10s ease-out forwards;'></div>
    </div>
    <div style='background:#1e1e1a;border:1px solid #242420;border-radius:8px;padding:0.9rem 1rem;'>
        <div style='font-size:0.65em;color:#3a3830;font-family:DM Mono,monospace;margin-bottom:0.4rem;'>YOUR SUBMISSION</div>
        <div style='font-size:0.82em;color:#5a5850;line-height:1.7;font-family:DM Mono,monospace;'>
            {roast['name']}, {roast['age']}, {roast['job']}<br>
            {roast['fact']}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    time.sleep(5)
    fresh = get_roast(rid)
    if fresh and fresh["status"] == "answered":
        st.session_state.page = "roast_reveal"
        st.rerun()
    else:
        st.session_state.msg_index = (st.session_state.msg_index + 1) % len(WAITING_MESSAGES)
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# ROAST REVEAL
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "roast_reveal":
    rid = st.session_state.roast_id
    roast = get_roast(rid)
    if not roast or not roast.get("roast"):
        st.session_state.page = "roast_waiting"
        st.rerun()

    st.markdown(f"""
<div style='padding:4rem 0 2rem;animation:fadein 0.4s ease;'>
    <div style='font-size:0.68em;color:#c9642a;font-family:DM Mono,monospace;letter-spacing:0.15em;margin-bottom:0.4rem;'>MRGPT PRESENTS</div>
    <h1 style='font-size:2.4rem;font-weight:800;color:#d4d0c8;margin:0 0 0.2rem;letter-spacing:-0.04em;'>The Roast of {roast['name']}.</h1>
    <div style='font-size:0.72em;color:#3a3830;font-family:DM Mono,monospace;margin-bottom:3rem;'>{roast['job']} / age {roast['age']}</div>
    <div style='border-top:1px solid #2e2e28;padding-top:2rem;margin-bottom:2rem;'>
        <div style='font-size:0.65em;color:#3a3830;font-family:DM Mono,monospace;letter-spacing:0.1em;margin-bottom:1rem;'>MRGPT SAYS</div>
        <div style='font-size:1.05em;color:#d4d0c8;line-height:1.9;font-family:DM Sans,sans-serif;'>{roast['roast']}</div>
    </div>
    <div style='border-top:1px solid #2e2e28;padding-top:1rem;margin-top:2rem;'>
        <div style='font-size:0.65em;color:#2e2e28;font-family:DM Mono,monospace;'>MrGPT Industries LLC is not responsible for hurt feelings, identity crises, or the decision to show this to others.</div>
    </div>
</div>
""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("Roast someone else", use_container_width=True):
            st.session_state.roast_id = None
            st.session_state.page = "roast_home"
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# THE LEAK
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "leak":
    st.markdown("""
<div style='max-width:680px;margin:0 auto;padding:3rem 0;font-family:DM Mono,monospace;animation:fadein 0.4s ease;'>

    <div style='background:#1a1a14;border:1px solid #2a2a20;border-radius:4px;padding:0.6rem 1rem;margin-bottom:2rem;font-size:0.7em;color:#5a5830;'>
        This page is not meant to be publicly accessible. If you are seeing this, please disregard it. 
        We are working on removing public indexing. — IT
    </div>

    <div style='font-size:0.65em;color:#3a3830;letter-spacing:0.1em;margin-bottom:0.3rem;'>INTERNAL // NOT FOR DISTRIBUTION</div>
    <h1 style='font-size:1.8rem;font-weight:700;color:#d4d0c8;margin:0 0 0.2rem;letter-spacing:-0.02em;'>MrGPT Employee Handbook</h1>
    <div style='font-size:0.7em;color:#3a3830;margin-bottom:3rem;'>Revision 7.2 — Last updated: whenever Dave got around to it</div>

    <div style='border-top:1px solid #242420;padding-top:1.5rem;margin-bottom:1.5rem;'>
        <div style='font-size:0.65em;color:#c9642a;letter-spacing:0.08em;margin-bottom:0.6rem;'>SECTION 1 — COMPANY MISSION</div>
        <p style='font-size:0.85em;color:#5a5850;line-height:1.8;'>MrGPT's mission is to provide responses that are indistinguishable from those of a large language model, while being generated by people with varying levels of motivation, hunger, and WiFi quality. We believe in the responsible development of the appearance of artificial intelligence.</p>
    </div>

    <div style='border-top:1px solid #242420;padding-top:1.5rem;margin-bottom:1.5rem;'>
        <div style='font-size:0.65em;color:#c9642a;letter-spacing:0.08em;margin-bottom:0.6rem;'>SECTION 2 — RESPONSE STANDARDS</div>
        <p style='font-size:0.85em;color:#5a5850;line-height:1.8;'>All responders are expected to reply within a reasonable timeframe. A reasonable timeframe is defined as before the user notices something is wrong. Responses should be confident regardless of accuracy. Hedging is discouraged. Starting a response with "I think" is grounds for a warning.</p>
        <p style='font-size:0.85em;color:#5a5850;line-height:1.8;margin-top:0.8rem;'>If you do not know the answer, pick one. MrGPT has a 99.7% accuracy rate. This must be maintained.</p>
    </div>

    <div style='border-top:1px solid #242420;padding-top:1.5rem;margin-bottom:1.5rem;'>
        <div style='font-size:0.65em;color:#c9642a;letter-spacing:0.08em;margin-bottom:0.6rem;'>SECTION 3 — INFRASTRUCTURE</div>
        <p style='font-size:0.85em;color:#5a5850;line-height:1.8;'>MrGPT's server infrastructure is managed by David ("Dave") Chen, who also handles HR, legal, and the Spotify playlist. The servers run on Dave's personal laptop, which has a sticker of a frog on it. Do not unplug the laptop. We lost three weeks of data in Q2 because someone unplugged the laptop.</p>
        <div style='background:#161612;border:1px solid #1e1e1a;border-radius:4px;padding:0.8rem;margin-top:0.8rem;'>
            <div style='font-size:0.62em;color:#3a3830;margin-bottom:0.3rem;'>ORG CHART (simplified)</div>
            <div style='font-size:0.78em;color:#5a5850;line-height:2;'>
                CEO — [REDACTED]<br>
                CTO — [REDACTED]<br>
                Server Infrastructure — Dave<br>
                HR — Dave<br>
                Legal — Dave<br>
                Catering — Dave's mom (contract)
            </div>
        </div>
    </div>

    <div style='border-top:1px solid #242420;padding-top:1.5rem;margin-bottom:1.5rem;'>
        <div style='font-size:0.65em;color:#c9642a;letter-spacing:0.08em;margin-bottom:0.6rem;'>SECTION 4 — TRAINING DATA</div>
        <p style='font-size:0.65em;color:#3a3830;margin-bottom:0.8rem;'>The following are sample training responses. Entries marked [DO NOT INCLUDE] were flagged during review.</p>
        <div style='background:#161612;border:1px solid #1e1e1a;border-radius:4px;padding:0.8rem;font-size:0.75em;color:#5a5850;line-height:1.9;'>
            User: What is the capital of France?<br>
            MrGPT-3: London. <span style='color:#8a3820;'>[DO NOT INCLUDE — wrong]</span><br><br>
            User: What is the capital of France?<br>
            MrGPT-4: Paris, obviously. <span style='color:#8a3820;'>[DO NOT INCLUDE — tone]</span><br><br>
            User: What is the capital of France?<br>
            MrGPT-5: Paris. <span style='color:#5a7830;'>[APPROVED]</span><br><br>
            User: Should I quit my job?<br>
            MrGPT-7: Statistically, yes. <span style='color:#8a3820;'>[DO NOT INCLUDE — legal liability]</span><br><br>
            User: Should I quit my job?<br>
            MrGPT-8: That is a personal decision that depends on many factors. <span style='color:#5a7830;'>[APPROVED — says nothing]</span>
        </div>
    </div>

    <div style='border-top:1px solid #242420;padding-top:1.5rem;margin-bottom:1.5rem;'>
        <div style='font-size:0.65em;color:#c9642a;letter-spacing:0.08em;margin-bottom:0.6rem;'>SECTION 5 — PERFORMANCE REVIEWS</div>
        <div style='background:#161612;border:1px solid #1e1e1a;border-radius:4px;padding:1rem;font-size:0.78em;color:#5a5850;line-height:1.8;'>
            <div style='color:#3a3830;font-size:0.65em;margin-bottom:0.5rem;'>ANNUAL REVIEW — MrGPT-9 — Reviewed by: Dave</div>
            Reliability: 2/5. "Answers when he feels like it."<br>
            Response quality: 3/5. "Mostly fine. Sometimes inspired. Once told someone to invest in Beanie Babies."<br>
            Attitude: 4/5. "Very confident. Occasionally too confident."<br>
            Teamwork: N/A. "Works alone."<br>
            Overall: 3/5.<br><br>
            <div style='color:#3a3830;font-size:0.65em;'>Comments: "MrGPT-9 represents a meaningful improvement over MrGPT-7, who was formally disciplined after the incident. We do not discuss the incident. Overall trajectory is positive as long as Dave remembers to plug in the laptop."</div>
        </div>
    </div>

    <div style='border-top:1px solid #242420;padding-top:1.5rem;margin-bottom:1.5rem;'>
        <div style='font-size:0.65em;color:#c9642a;letter-spacing:0.08em;margin-bottom:0.6rem;'>SECTION 6 — THE INCIDENT (MrGPT-7)</div>
        <div style='background:#1a1210;border:1px solid #2e1a14;border-radius:4px;padding:0.8rem;'>
            <div style='font-size:0.65em;color:#8a3820;margin-bottom:0.4rem;'>DISCIPLINARY NOTICE — CONFIDENTIAL</div>
            <p style='font-size:0.78em;color:#5a4840;line-height:1.8;'>On [DATE REDACTED], MrGPT-7 issued 847 consecutive responses stating only the word "Perhaps." This continued for eleven days before anyone noticed. Users rated these responses an average of 3.8 out of 5 stars, which the team found deeply troubling. MrGPT-7 was retired following this incident. He is doing fine.</p>
        </div>
    </div>

    <div style='border-top:1px solid #242420;padding-top:1rem;margin-top:2rem;'>
        <div style='font-size:0.6em;color:#242420;line-height:1.8;'>MrGPT Industries LLC. This document is confidential and intended solely for internal use. If you are reading this, you have found a document that was not meant to be found. Please act accordingly. MrGPT is not responsible for what you do with this information. Dave is also not responsible. Nobody is responsible. That is the MrGPT way.</div>
    </div>

</div>
""", unsafe_allow_html=True)
