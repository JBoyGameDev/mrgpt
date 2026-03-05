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

PERSONAS = {
    "default": {
        "name": "MrGPT",
        "title": "General AI Assistant",
        "avatar": "🤖",
        "desc": "Ask me anything.",
        "model": "MrGPT-9 Turbo Ultra Pro Max",
    },
    "coach": {
        "name": "Coach GPT",
        "title": "Life Coach & Motivational AI",
        "avatar": "💪",
        "desc": "Ready to unlock your potential.",
        "model": "CoachGPT-Elite v3",
    },
    "chef": {
        "name": "Chef GPT",
        "title": "Culinary Intelligence System",
        "avatar": "👨‍🍳",
        "desc": "Ask me about food, recipes, or dinner.",
        "model": "ChefGPT-Michelin Edition",
    },
    "advisor": {
        "name": "Finance GPT",
        "title": "AI Financial Advisor",
        "avatar": "📈",
        "desc": "Your money, my algorithms.",
        "model": "FinanceGPT-WallStreet Pro",
    },
}

WAITING_MESSAGES = [
    ("MrGPT is playing Minecraft right now.", "He'll answer you between rounds."),
    ("MrGPT is asleep.", "His dedication to your question is truly inspiring."),
    ("MrGPT is eating.", "Do not disturb. Seriously."),
    ("MrGPT has seen your message.", "He left it on read. Intentionally."),
    ("MrGPT stepped outside for some air.", "In January. Without a jacket."),
    ("MrGPT is watching YouTube.", "For research purposes."),
    ("MrGPT is arguing with someone online.", "Your question is next. Probably."),
    ("MrGPT is in the bathroom.", "This could take anywhere from 2 to 45 minutes."),
    ("MrGPT is making a playlist.", "Very relevant to your question, trust."),
    ("Consulting the ancient texts.", "It's Reddit."),
    ("MrGPT battery: 2%.", "Peak performance mode activated."),
    ("MrGPT is mentally on vacation.", "Physically at his desk. Spiritually? Gone."),
    ("BEEP BOOP PROCESSING.", "This is definitely a real AI and not a person."),
    ("You are number 1 in queue.", "Queue currently has 847 other questions."),
    ("MrGPT has entered sleep mode.", "Expected wake time: unknown."),
    ("MrGPT is thinking really hard.", "Or he forgot. Hard to tell."),
    ("Running at 12% capacity.", "This IS peak performance."),
    ("MrGPT rolled a die to decide.", "He got a 3. Whatever that means."),
    ("Neural pathways activating.", "Nothing is happening. We are working on it."),
    ("Transmitting across the servers.", "The servers are a guy named Dave."),
    ("MrGPT is getting coffee.", "Fourth cup today. He is fine."),
    ("Answers at the speed of thought.", "MrGPT thinks quite slowly."),
    ("Cross-referencing 47 billion data points.", "The data points are vibes."),
    ("MrGPT is pondering your question.", "He finds it deeply confusing."),
    ("Loading.", "Has been loading since 2019."),
    ("MrGPT is feeding ducks.", "This is relevant to your query somehow."),
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

def new_conversation(persona_key):
    data = get_data()
    cid = str(uuid.uuid4())[:8].upper()
    data["conversations"][cid] = {
        "id": cid,
        "persona": persona_key,
        "messages": [],
        "revealed": False,
        "created_at": datetime.now().isoformat(),
    }
    # Prune old conversations
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
        "id": mid,
        "question": question_text,
        "answer": None,
        "status": "pending",
        "rating": None,
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
        "id": "REVEAL",
        "question": None,
        "answer": "By the way — I'm not actually an AI. I'm a real person who has been answering your questions this whole time. Hope that was fun. 👋",
        "status": "answered",
        "rating": None,
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

st.set_page_config(page_title="MrGPT", page_icon="🤖", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, .stApp { background-color: #0f1117; color: #e8e8f0; font-family: 'Space Grotesk', ui-sans-serif, system-ui, sans-serif; }
.block-container { max-width: 780px !important; padding: 0 2rem !important; margin: 0 auto; }
#MainMenu, footer { visibility: hidden; }
header { background: transparent !important; }

[data-testid="stSidebar"] { background: #090b10 !important; border-right: 1px solid #1a1d2e; }
[data-testid="stSidebar"] .block-container { padding: 1.2rem 0.9rem !important; max-width: 100% !important; }
[data-testid="stSidebarContent"] { padding: 0 !important; }

[data-testid="stSidebar"] .stButton > button {
    background: transparent; color: #666; border: none; border-radius: 8px;
    font-size: 0.85em; font-weight: 400; padding: 0.5rem 0.75rem;
    text-align: left; width: 100%; transition: all 0.12s;
    font-family: 'Space Grotesk', sans-serif;
}
[data-testid="stSidebar"] .stButton > button:hover { background: #13162a; color: #e8e8f0; }

section.main .stButton > button {
    background: #13162a; color: #e8e8f0; border: 1px solid #1e2240;
    border-radius: 10px; font-family: 'Space Grotesk', sans-serif;
    font-weight: 500; font-size: 0.92em; letter-spacing: 0.01em;
    padding: 0.65em 1.3em; transition: all 0.15s; width: 100%;
}
section.main .stButton > button:hover { background: #1a1f38; border-color: #2a3060; transform: translateY(-1px); }

.stTextArea textarea {
    background: #13162a; border: 1.5px solid #1e2240; border-radius: 18px;
    color: #e8e8f0; font-family: 'Space Grotesk', sans-serif;
    font-size: 1em; line-height: 1.65; padding: 1.1rem 1.3rem; resize: none;
    transition: border-color 0.15s, box-shadow 0.15s;
}
.stTextArea textarea:focus { border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,0.12); outline: none; }
.stTextArea textarea::placeholder { color: #333852; }

.stTextInput input {
    background: #13162a !important; border: 1.5px solid #1e2240 !important;
    border-radius: 10px !important; color: #e8e8f0 !important;
    font-family: 'Space Grotesk', sans-serif !important;
}
.stTextInput input:focus { border-color: #3b82f6 !important; box-shadow: 0 0 0 3px rgba(59,130,246,0.12) !important; }
.stTextInput input::placeholder { color: #333852 !important; }

[data-testid="stContainer"] { background: #13162a; border: 1px solid #1e2240; border-radius: 14px; }
[data-testid="stExpander"] { background: #0d1020; border: 1px solid #1a1d2e; border-radius: 10px; }
hr { border-color: #1a1d2e !important; }

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #090b10; }
::-webkit-scrollbar-thumb { background: #1e2240; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #2a3060; }

@keyframes fadein { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }
@keyframes blink { 0%,100% { opacity: 1; } 50% { opacity: 0; } }
@keyframes pulse-dot { 0%,100% { opacity: 0.3; transform: scale(0.7); } 50% { opacity: 1; transform: scale(1); } }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
@keyframes float-slow { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-6px); } }
@keyframes progress-stuck { 0% { width: 0%; } 55% { width: 94%; } 70% { width: 97%; } 100% { width: 97%; } }
@keyframes shimmer { 0% { background-position: -200% center; } 100% { background-position: 200% center; } }
</style>
""", unsafe_allow_html=True)

for k, v in [
    ("page", "home"), ("conv_id", None), ("persona", "default"),
    ("show_admin_input", False), ("chat_history", []),
    ("pending_mid", None), ("msg_index", 0),
]:
    if k not in st.session_state:
        st.session_state[k] = v

params = st.query_params
is_admin = params.get("admin", "") == ADMIN_KEY

# Load conversation from URL param
url_conv = params.get("id", "")
if url_conv and not st.session_state.conv_id:
    st.session_state.conv_id = url_conv.upper()
    st.session_state.page = "chat"

with st.sidebar:
    persona = PERSONAS[st.session_state.persona]
    st.markdown(f"""
<div style='padding:0.4rem 0.2rem 1.2rem;'>
    <div style='display:flex;align-items:center;gap:0.7rem;margin-bottom:0.9rem;'>
        <div style='width:32px;height:32px;background:linear-gradient(135deg,#3b82f6,#1d4ed8);
            border-radius:9px;display:flex;align-items:center;justify-content:center;
            font-size:1rem;flex-shrink:0;box-shadow:0 4px 12px rgba(59,130,246,0.3);'>
            {persona["avatar"]}
        </div>
        <span style='font-weight:700;font-size:1.05em;color:#e8e8f0;font-family:Space Grotesk,sans-serif;letter-spacing:-0.01em;'>MrGPT</span>
    </div>
    <div style='background:#13162a;border:1px solid #1e2240;border-radius:8px;
        padding:0.35rem 0.7rem;font-size:0.7em;color:#444;
        display:flex;justify-content:space-between;align-items:center;
        font-family:Space Mono,monospace;'>
        <span>{persona["model"]}</span><span style='color:#222;'>▾</span>
    </div>
</div>
""", unsafe_allow_html=True)

    if st.button("✏️  New chat", key="sb_new", use_container_width=True):
        st.session_state.page = "home"
        st.session_state.conv_id = None
        st.session_state.pending_mid = None
        st.rerun()

    if st.button("ℹ️  About MrGPT", key="sb_about", use_container_width=True):
        st.session_state.page = "about"
        st.rerun()

    st.markdown("<hr style='border-color:#13162a;margin:0.5rem 0;'>", unsafe_allow_html=True)

    if st.session_state.chat_history:
        st.markdown("<div style='font-size:0.65em;color:#2a3060;padding:0 0.4rem 0.5rem;text-transform:uppercase;letter-spacing:0.08em;font-family:Space Mono,monospace;'>Recent</div>", unsafe_allow_html=True)
        for i, chat in enumerate(reversed(st.session_state.chat_history[-8:])):
            label = chat["question"][:28] + ("…" if len(chat["question"]) > 28 else "")
            if st.button(f"💬  {label}", key=f"hist_{i}", use_container_width=True):
                st.session_state.conv_id = chat["conv_id"]
                st.session_state.page = "chat"
                st.rerun()
    else:
        st.markdown("<div style='font-size:0.75em;color:#1a1d2e;padding:0.5rem;text-align:center;font-family:Space Mono,monospace;'>No chats yet</div>", unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#13162a;margin:0.5rem 0;'>", unsafe_allow_html=True)

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

# ── ADMIN ─────────────────────────────────────────────────────────────────────
if is_admin or st.session_state.page == "admin_verified":
    col_back, col_title, col_refresh = st.columns([1, 4, 1])
    with col_back:
        st.write("")
        if st.button("← Back", key="admin_back"):
            st.session_state.page = "home"
            st.rerun()
    with col_title:
        st.markdown("<div style='padding:0.4rem 0 1.2rem;'><div style='font-size:0.7em;color:#444;font-family:Space Mono,monospace;letter-spacing:0.08em;'>STAFF</div><div style='font-size:1.5em;font-weight:700;color:#e8e8f0;letter-spacing:-0.02em;'>Inbox</div></div>", unsafe_allow_html=True)
    with col_refresh:
        st.write("")
        if st.button("↻ Refresh", key="admin_refresh"):
            st.rerun()

    data = get_data()
    convos = data.get("conversations", {})
    active = [(cid, c) for cid, c in convos.items()
              if any(m["status"] == "pending" for m in c["messages"])]
    answered_convos = [(cid, c) for cid, c in convos.items()
                       if not any(m["status"] == "pending" for m in c["messages"]) and c["messages"]]

    if not active:
        st.markdown("<div style='text-align:center;padding:4rem 0;color:#2a3060;'><div style='font-size:2rem;margin-bottom:0.8rem;'>✓</div><div style='font-size:0.95em;font-family:Space Grotesk,sans-serif;'>All caught up. Go touch grass.</div></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='color:#3b82f6;font-size:0.78em;font-weight:600;margin-bottom:1.2rem;letter-spacing:0.08em;font-family:Space Mono,monospace;'>{len(active)} ACTIVE CONVERSATION(S)</div>", unsafe_allow_html=True)
        for cid, convo in active:
            p = PERSONAS.get(convo.get("persona", "default"), PERSONAS["default"])
            with st.container(border=True):
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    st.markdown(f"<div style='font-size:0.68em;color:#444;font-family:Space Mono,monospace;margin-bottom:0.3rem;'>{p['avatar']} {p['name']} · #{cid}</div>", unsafe_allow_html=True)
                with col_b:
                    if not convo.get("revealed"):
                        if st.button("👋 Reveal", key=f"reveal_{cid}"):
                            reveal_conversation(cid)
                            st.success("Truth revealed!")
                            time.sleep(0.5)
                            st.rerun()

                for m in convo["messages"]:
                    if m.get("is_reveal"):
                        continue
                    rating_str = ""
                    if m.get("rating") == "up":
                        rating_str = " 👍"
                    elif m.get("rating") == "down":
                        rating_str = " 👎"
                    if m["status"] == "answered":
                        st.markdown(f"<div style='padding:0.6rem 0.8rem;background:#0d1020;border-radius:8px;margin-bottom:0.5rem;'><div style='font-size:0.8em;color:#444;'>Q: {m['question']}</div><div style='font-size:0.85em;color:#e8e8f0;margin-top:0.2rem;'>A: {m['answer']}{rating_str}</div></div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div style='padding:0.7rem 0.9rem;background:#13162a;border:1px solid #3b82f6;border-radius:8px;margin-bottom:0.8rem;'><div style='font-size:0.72em;color:#3b82f6;font-family:Space Mono,monospace;margin-bottom:0.4rem;'>PENDING · #{m['id']}</div><div style='font-size:1.02em;color:#e8e8f0;font-weight:500;'>'{m['question']}'</div></div>", unsafe_allow_html=True)
                        ans = st.text_area("", key=f"ans_{cid}_{m['id']}", height=75,
                                           placeholder="Reply as MrGPT...", label_visibility="collapsed")
                        c1, c2, c3 = st.columns([4, 1, 1])
                        with c1:
                            if st.button("Send reply", key=f"sub_{cid}_{m['id']}", use_container_width=True):
                                if ans.strip():
                                    answer_message(cid, m["id"], ans.strip())
                                    st.success("Sent.")
                                    time.sleep(0.4)
                                    st.rerun()
                        with c2:
                            if st.button("✕", key=f"del_{cid}", use_container_width=True):
                                delete_conversation(cid)
                                st.rerun()

    if answered_convos:
        st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)
        with st.expander(f"History — {len(answered_convos)} closed conversations"):
            for cid, convo in reversed(answered_convos[-5:]):
                p = PERSONAS.get(convo.get("persona", "default"), PERSONAS["default"])
                st.markdown(f"<div style='font-size:0.68em;color:#444;font-family:Space Mono,monospace;margin-bottom:0.5rem;'>{p['avatar']} {p['name']} · #{cid}</div>", unsafe_allow_html=True)
                for m in convo["messages"]:
                    if m.get("answer"):
                        rating_str = " 👍" if m.get("rating") == "up" else (" 👎" if m.get("rating") == "down" else "")
                        st.markdown(f"<div style='padding:0.5rem 0.7rem;background:#0d1020;border-radius:6px;margin-bottom:0.4rem;'><div style='color:#444;font-size:0.78em;'>Q: {m['question'] or 'Reveal'}</div><div style='color:#e8e8f0;font-size:0.82em;margin-top:0.1rem;'>A: {m['answer']}{rating_str}</div></div>", unsafe_allow_html=True)
                st.markdown("<hr style='border-color:#1a1d2e;margin:0.8rem 0;'>", unsafe_allow_html=True)
    st.stop()

# ── ABOUT ─────────────────────────────────────────────────────────────────────
elif st.session_state.page == "about":
    st.markdown("<div style='padding:3rem 0 2rem;text-align:center;animation:fadein 0.4s ease;'><h1 style='font-size:2.1rem;font-weight:700;color:#e8e8f0;margin-bottom:0.3rem;letter-spacing:-0.03em;'>About MrGPT</h1><p style='color:#444;font-size:0.85em;font-family:Space Mono,monospace;'>The world's most advanced AI. Probably.</p></div>", unsafe_allow_html=True)
    st.markdown("""<div style='display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:2rem;'>
<div style='background:#13162a;border:1px solid #1e2240;border-radius:14px;padding:1.3rem;text-align:center;'>
<div style='font-size:2rem;font-weight:800;color:#3b82f6;font-family:Space Grotesk,sans-serif;'>1,847,293</div>
<div style='font-size:0.75em;color:#555;margin-top:0.2rem;'>Questions Answered</div>
<div style='font-size:0.58em;color:#1e2240;font-family:Space Mono,monospace;'>number completely made up</div></div>
<div style='background:#13162a;border:1px solid #1e2240;border-radius:14px;padding:1.3rem;text-align:center;'>
<div style='font-size:2rem;font-weight:800;color:#3b82f6;font-family:Space Grotesk,sans-serif;'>99.7%</div>
<div style='font-size:0.75em;color:#555;margin-top:0.2rem;'>Accuracy Rate</div>
<div style='font-size:0.58em;color:#1e2240;font-family:Space Mono,monospace;'>not measured</div></div>
<div style='background:#13162a;border:1px solid #1e2240;border-radius:14px;padding:1.3rem;text-align:center;'>
<div style='font-size:2rem;font-weight:800;color:#3b82f6;font-family:Space Grotesk,sans-serif;'>GPT-9</div>
<div style='font-size:0.75em;color:#555;margin-top:0.2rem;'>Model Version</div>
<div style='font-size:0.58em;color:#1e2240;font-family:Space Mono,monospace;'>ahead of OpenAI by several years</div></div>
<div style='background:#13162a;border:1px solid #1e2240;border-radius:14px;padding:1.3rem;text-align:center;'>
<div style='font-size:2rem;font-weight:800;color:#3b82f6;font-family:Space Grotesk,sans-serif;'>&lt;infms</div>
<div style='font-size:0.75em;color:#555;margin-top:0.2rem;'>Response Time</div>
<div style='font-size:0.58em;color:#1e2240;font-family:Space Mono,monospace;'>technically true</div></div>
</div>
<div style='background:#13162a;border:1px solid #1e2240;border-radius:14px;padding:1.5rem;'>
<div style='font-size:0.72em;font-weight:600;color:#3b82f6;margin-bottom:0.8rem;text-transform:uppercase;letter-spacing:0.08em;font-family:Space Mono,monospace;'>About Our Technology</div>
<p style='color:#888;font-size:0.9em;line-height:1.75;font-family:Space Grotesk,sans-serif;'>MrGPT is powered by our proprietary Neural Cognition Engine, trained on over 47 billion data points gathered from across the internet, several encyclopedias, and at least one fortune cookie.</p>
<p style='color:#333;font-size:0.65em;margin-top:0.8rem;font-family:Space Mono,monospace;'>MrGPT Industries LLC is not responsible for any advice given, consequences thereof, or feelings of confusion.</p>
</div>""", unsafe_allow_html=True)

# ── HOME ──────────────────────────────────────────────────────────────────────
elif st.session_state.page == "home":
    st.markdown("<div style='text-align:center;padding:4rem 0 2rem;animation:fadein 0.4s ease;'><div style='width:58px;height:58px;background:linear-gradient(135deg,#3b82f6,#1d4ed8);border-radius:16px;display:inline-flex;align-items:center;justify-content:center;font-size:1.8rem;margin-bottom:1.2rem;box-shadow:0 8px 32px rgba(59,130,246,0.3);animation:float-slow 3s ease-in-out infinite;'>🤖</div><h1 style='font-size:2.1rem;font-weight:700;color:#e8e8f0;margin:0 0 0.5rem;letter-spacing:-0.03em;font-family:Space Grotesk,sans-serif;'>What can I help with?</h1><p style='color:#333852;font-size:0.85em;margin:0;font-family:Space Mono,monospace;'>Powered by MrGPT Neural Engine v9.4</p></div>", unsafe_allow_html=True)

    st.markdown("<div style='font-size:0.82em;color:#444;font-weight:500;margin-bottom:0.6rem;'>Choose a persona:</div>", unsafe_allow_html=True)
    cols = st.columns(4)
    for i, (pkey, pdata) in enumerate(PERSONAS.items()):
        with cols[i]:
            selected = st.session_state.persona == pkey
            border_color = "#3b82f6" if selected else "#1e2240"
            bg_color = "#13162a" if selected else "#0d1020"
            st.markdown(f"<div style='background:{bg_color};border:1.5px solid {border_color};border-radius:12px;padding:0.8rem;text-align:center;cursor:pointer;margin-bottom:0.3rem;'><div style='font-size:1.5rem;'>{pdata['avatar']}</div><div style='font-size:0.75em;font-weight:600;color:#e8e8f0;margin-top:0.3rem;'>{pdata['name']}</div><div style='font-size:0.62em;color:#444;margin-top:0.1rem;'>{pdata['desc']}</div></div>", unsafe_allow_html=True)
            if st.button("Select", key=f"p_{pkey}", use_container_width=True):
                st.session_state.persona = pkey
                st.rerun()

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    question = st.text_area("", placeholder="Message MrGPT...", height=110, label_visibility="collapsed")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Send message", use_container_width=True):
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

    st.markdown("<div style='display:flex;flex-wrap:wrap;gap:0.5rem;justify-content:center;margin-top:1.2rem;'><div style='background:#13162a;border:1px solid #1e2240;border-radius:20px;padding:0.4rem 1rem;font-size:0.78em;color:#666;font-family:Space Grotesk,sans-serif;'>Explain something</div><div style='background:#13162a;border:1px solid #1e2240;border-radius:20px;padding:0.4rem 1rem;font-size:0.78em;color:#666;font-family:Space Grotesk,sans-serif;'>Give me ideas</div><div style='background:#13162a;border:1px solid #1e2240;border-radius:20px;padding:0.4rem 1rem;font-size:0.78em;color:#666;font-family:Space Grotesk,sans-serif;'>Ask anything</div><div style='background:#13162a;border:1px solid #1e2240;border-radius:20px;padding:0.4rem 1rem;font-size:0.78em;color:#666;font-family:Space Grotesk,sans-serif;'>Help me decide</div></div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center;margin-top:3rem;color:#1a1d2e;font-size:0.7em;font-family:Space Mono,monospace;'>MrGPT can make mistakes. Consider checking important info.</div>", unsafe_allow_html=True)

# ── CHAT PAGE ─────────────────────────────────────────────────────────────────
elif st.session_state.page == "chat":
    cid = st.session_state.conv_id
    if not cid:
        st.session_state.page = "home"
        st.rerun()

    convo = get_conversation(cid)
    if not convo:
        st.warning("Conversation not found.")
        st.session_state.page = "home"
        st.rerun()

    persona = PERSONAS.get(convo.get("persona", "default"), PERSONAS["default"])
    messages = convo.get("messages", [])
    answered = [m for m in messages if m["status"] == "answered"]
    pending = [m for m in messages if m["status"] == "pending"]

    st.markdown(f"<div style='padding:1.5rem 0 1rem;border-bottom:1px solid #1a1d2e;margin-bottom:1.5rem;display:flex;align-items:center;gap:0.8rem;'><div style='width:38px;height:38px;background:linear-gradient(135deg,#3b82f6,#1d4ed8);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.2rem;box-shadow:0 4px 12px rgba(59,130,246,0.25);'>{persona['avatar']}</div><div><div style='font-weight:700;color:#e8e8f0;font-family:Space Grotesk,sans-serif;'>{persona['name']}</div><div style='font-size:0.72em;color:#444;font-family:Space Mono,monospace;'>{persona['title']}</div></div></div>", unsafe_allow_html=True)

    # Share ID
    st.markdown(f"<div style='background:#0d1020;border:1px solid #1e2240;border-radius:8px;padding:0.5rem 1rem;margin-bottom:1.2rem;display:flex;justify-content:space-between;align-items:center;'><span style='font-size:0.7em;color:#333852;font-family:Space Mono,monospace;'>Share this chat:</span><span style='font-size:0.78em;font-weight:700;color:#3b82f6;font-family:Space Mono,monospace;letter-spacing:0.08em;'>{cid}</span></div>", unsafe_allow_html=True)

    # Render messages
    for m in messages:
        if m.get("is_reveal"):
            st.markdown(f"<div style='background:#13162a;border:1.5px solid #3b82f6;border-radius:12px;padding:1rem 1.2rem;margin:1rem 0;text-align:center;animation:fadein 0.4s ease;'><div style='font-size:0.7em;color:#3b82f6;font-family:Space Mono,monospace;margin-bottom:0.4rem;'>SYSTEM MESSAGE</div><div style='color:#e8e8f0;font-size:0.95em;line-height:1.6;'>{m['answer']}</div></div>", unsafe_allow_html=True)
            continue

        if m.get("question"):
            st.markdown(f"<div style='display:flex;justify-content:flex-end;margin:0.8rem 0;animation:fadein 0.3s ease;'><div style='background:#13162a;border:1px solid #1e2240;border-radius:18px 18px 4px 18px;padding:0.85rem 1.15rem;max-width:78%;color:#e8e8f0;font-size:0.95em;line-height:1.65;font-family:Space Grotesk,sans-serif;'>{m['question']}</div></div>", unsafe_allow_html=True)

        if m["status"] == "answered" and m.get("answer"):
            st.markdown(f"<div style='display:flex;align-items:flex-start;gap:0.8rem;margin:0.8rem 0;animation:fadein 0.4s ease;'><div style='width:34px;height:34px;min-width:34px;background:linear-gradient(135deg,#3b82f6,#1d4ed8);border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:1rem;box-shadow:0 2px 10px rgba(59,130,246,0.3);margin-top:2px;'>{persona['avatar']}</div><div style='flex:1;'><div style='font-size:0.75em;font-weight:600;color:#555;margin-bottom:0.5rem;font-family:Space Mono,monospace;'>{persona['name']}</div><div style='color:#e8e8f0;font-size:0.96em;line-height:1.75;font-family:Space Grotesk,sans-serif;'>{m['answer']}</div></div></div>", unsafe_allow_html=True)

            # Rating
            if m.get("rating") is None and not m.get("is_reveal") and m["id"] != "REVEAL":
                col1, col2, col3 = st.columns([1, 3, 1])
                with col2:
                    rc1, rc2, rc3 = st.columns([1, 1, 4])
                    with rc1:
                        if st.button("👍", key=f"up_{m['id']}"):
                            rate_message(cid, m["id"], "up")
                            st.rerun()
                    with rc2:
                        if st.button("👎", key=f"dn_{m['id']}"):
                            rate_message(cid, m["id"], "down")
                            st.rerun()
            elif m.get("rating"):
                icon = "👍" if m["rating"] == "up" else "👎"
                st.markdown(f"<div style='font-size:0.72em;color:#333852;padding:0 0 0.5rem 3rem;'>{icon}</div>", unsafe_allow_html=True)

        elif m["status"] == "pending":
            # Waiting screen — SIMPLE text only, no HTML shapes
            headline, subline = WAITING_MESSAGES[st.session_state.msg_index % len(WAITING_MESSAGES)]
            st.markdown(f"""
<div style='display:flex;align-items:flex-start;gap:0.8rem;margin:0.8rem 0;animation:fadein 0.4s ease;'>
    <div style='width:34px;height:34px;min-width:34px;background:linear-gradient(135deg,#3b82f6,#1d4ed8);border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:1rem;box-shadow:0 2px 10px rgba(59,130,246,0.3);margin-top:2px;'>{persona['avatar']}</div>
    <div style='flex:1;'>
        <div style='font-size:0.75em;font-weight:600;color:#555;margin-bottom:0.5rem;font-family:Space Mono,monospace;'>{persona['name']}</div>
        <div style='background:#13162a;border:1px solid #1e2240;border-radius:4px 18px 18px 18px;padding:1.5rem 1.4rem;'>
            <div style='font-size:1.4rem;font-weight:700;color:#e8e8f0;margin-bottom:0.3rem;font-family:Space Grotesk,sans-serif;'>{headline}</div>
            <div style='font-size:0.88em;color:#555;margin-bottom:1.2rem;font-family:Space Grotesk,sans-serif;'>{subline}</div>
            <div style='background:#0d1020;border-radius:100px;height:3px;overflow:hidden;max-width:200px;'>
                <div style='height:100%;background:linear-gradient(90deg,#3b82f6,#60a5fa);animation:progress-stuck 8s ease-out forwards;box-shadow:0 0 6px rgba(59,130,246,0.6);'></div>
            </div>
            <div style='font-size:0.62em;color:#2a3060;margin-top:0.5rem;font-family:Space Mono,monospace;animation:blink 2s infinite;'>processing...</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

            # Typing dots
            st.markdown("<div style='display:flex;align-items:center;gap:0.35rem;padding:0 0 0.5rem 3rem;'><div style='width:6px;height:6px;background:#1e2240;border-radius:50%;animation:pulse-dot 1.2s ease-in-out infinite;'></div><div style='width:6px;height:6px;background:#1e2240;border-radius:50%;animation:pulse-dot 1.2s ease-in-out 0.2s infinite;'></div><div style='width:6px;height:6px;background:#1e2240;border-radius:50%;animation:pulse-dot 1.2s ease-in-out 0.4s infinite;'></div></div>", unsafe_allow_html=True)

            # Poll
            time.sleep(5)
            fresh = get_conversation(cid)
            fresh_msg = next((x for x in fresh["messages"] if x["id"] == m["id"]), None)
            if fresh_msg and fresh_msg["status"] == "answered":
                st.session_state.msg_index = random.randint(0, len(WAITING_MESSAGES) - 1)
                st.rerun()
            else:
                st.session_state.msg_index = (st.session_state.msg_index + 1) % len(WAITING_MESSAGES)
                st.rerun()

    # New message input
    if not pending and not convo.get("revealed"):
        msg_count = len([m for m in messages if not m.get("is_reveal")])
        if msg_count < MAX_MESSAGES:
            st.markdown(f"<div style='margin-top:1rem;height:1px;background:#1a1d2e;'></div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:0.68em;color:#2a3060;text-align:right;font-family:Space Mono,monospace;margin:0.4rem 0;'>{msg_count}/{MAX_MESSAGES} messages</div>", unsafe_allow_html=True)
            followup = st.text_area("", placeholder="Ask a follow-up...", height=90, label_visibility="collapsed", key="followup")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("Send", use_container_width=True, key="send_followup"):
                    if followup.strip():
                        mid = add_message(cid, followup.strip())
                        st.session_state.pending_mid = mid
                        st.session_state.msg_index = random.randint(0, len(WAITING_MESSAGES) - 1)
                        st.rerun()
                    else:
                        st.warning("Type something first.")
        else:
            st.markdown("<div style='text-align:center;padding:1.5rem;color:#2a3060;font-size:0.85em;font-family:Space Mono,monospace;'>Chat limit reached. Start a new chat to continue.</div>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("New chat", use_container_width=True):
                    st.session_state.page = "home"
                    st.session_state.conv_id = None
                    st.rerun()

    st.markdown("<div style='text-align:center;color:#1a1d2e;font-size:0.68em;margin-top:2rem;font-family:Space Mono,monospace;'>MrGPT can make mistakes. Consider checking important info.</div>", unsafe_allow_html=True)
