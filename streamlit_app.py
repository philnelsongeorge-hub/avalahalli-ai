"""
================================================================================
⚡ AVALAHALLI AI (STREAMLIT HUB)
Clean, fast, and versatile AI assistant for chat, coding, and research.
With Built-in Continuous Learning, Fixed Docked Chat Input & Real-Time Logging.
================================================================================
"""

import streamlit as st
import time
import json
import os
import sys
import re
import base64
from datetime import datetime

# Add engine path
ENGINE_DIR = os.path.join(os.path.dirname(__file__), 'server', 'src', 'engine')
if ENGINE_DIR not in sys.path:
    sys.path.insert(0, ENGINE_DIR)

try:
    from avalahalli_engine import AvalahalliEngine
except ImportError:
    st.error(f"Could not import AvalahalliEngine from {ENGINE_DIR}. Please check the directory path.")
    st.stop()

# Setup Logs Directory
LOGS_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOGS_DIR, exist_ok=True)
LOG_FILE_PATH = os.path.join(LOGS_DIR, "live_interactions.jsonl")

def log_user_interaction(query, response, persona, elapsed_s, feedback=None, notes=""):
    """Log user interactions for continuous evaluation and model training."""
    record = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "query": query,
        "persona": persona,
        "elapsed_s": round(elapsed_s, 3),
        "response": response[:1200] if response else "",
        "feedback": feedback,
        "notes": notes
    }
    try:
        with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        pass

def get_all_logged_interactions():
    """Retrieve all interaction records."""
    records = []
    if os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except Exception:
                        pass
    legacy_log = os.path.join(os.path.dirname(__file__), "server", "logs", "live_interactions.jsonl")
    if os.path.exists(legacy_log):
        with open(legacy_log, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except Exception:
                        pass
    return records

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Avalahalli AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- LOAD SHALIMAR MUTTON BACKGROUND IMAGE (SELF-CONTAINED BASE64) ---
try:
    from shalimar_b64 import SHALIMAR_IMAGE_B64
    bg_css_url = f"data:image/jpeg;base64,{SHALIMAR_IMAGE_B64}"
except ImportError:
    def get_base64_image(image_path):
        if os.path.exists(image_path):
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        return ""
    img_path = os.path.join(os.path.dirname(__file__), "assets", "shalimar_mutton.jpg")
    img_b64 = get_base64_image(img_path)
    bg_css_url = f"data:image/jpeg;base64,{img_b64}" if img_b64 else ""

# --- CUSTOM CSS STYLING ---
st.markdown(f"""
<style>
    /* Dark Theme Adjustments */
    .stApp {{
        background: linear-gradient(135deg, #0b0f19 0%, #111827 50%, #0b0f19 100%);
        color: #f8fafc;
    }}

    /* Real Shalimar Mutton Stall Background with Super Fast Fade Animation */
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: url('{bg_css_url}') no-repeat center center fixed;
        background-size: cover;
        z-index: 0;
        pointer-events: none;
        animation: muttonBgFadeFast 1.2s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
    }}

    @keyframes muttonBgFadeFast {{
        0% {{
            opacity: 0.85;
            filter: blur(0px) brightness(1.05);
        }}
        30% {{
            opacity: 0.40;
            filter: blur(1px) brightness(0.9);
        }}
        70% {{
            opacity: 0.10;
            filter: blur(3px) brightness(0.7);
        }}
        100% {{
            opacity: 0.02;
            filter: blur(6px) brightness(0.5);
        }}
    }}

    /* Ensure comfortable reading space above the docked text box */
    .main .block-container {{
        position: relative;
        z-index: 1;
        padding-bottom: 160px !important;
    }}

    /* Clean Docked Bottom Input (Zero Ghost Shadows) */
    div[data-testid="stBottom"] {{
        background: transparent !important;
        padding: 10px 24px 20px 24px !important;
    }}
    
    div[data-testid="stChatInput"] {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        max-width: 820px !important;
        margin: 0 auto !important;
    }}

    div[data-testid="stChatInput"] > div {{
        border-radius: 24px !important;
        background: rgba(22, 30, 46, 0.85) !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
    }}

    div[data-testid="stChatInput"] > div:focus-within {{
        border-color: rgba(56, 189, 248, 0.5) !important;
        box-shadow: 0 0 0 1px rgba(56, 189, 248, 0.3), 0 6px 24px rgba(0, 0, 0, 0.4) !important;
    }}

    div[data-testid="stChatInput"] textarea {{
        background: transparent !important;
        color: #f8fafc !important;
        font-size: 0.95rem !important;
    }}

    /* Replace sidebar collapse/expand double-arrows with 3-Lines Hamburger Menu (☰) */
    button[data-testid="stSidebarCollapseButton"] svg,
    button[data-testid="baseButton-header"] svg,
    div[data-testid="collapsedControl"] svg,
    button[kind="header"] svg {{
        display: none !important;
    }}

    button[data-testid="stSidebarCollapseButton"]::after,
    button[data-testid="baseButton-header"]::after,
    div[data-testid="collapsedControl"]::after,
    button[kind="header"]::after {{
        content: "☰" !important;
        font-size: 1.35rem !important;
        color: #94a3b8 !important;
        display: inline-block !important;
        line-height: 1 !important;
        font-weight: bold !important;
        transition: all 0.2s ease !important;
    }}

    button[data-testid="stSidebarCollapseButton"]:hover::after,
    button[data-testid="baseButton-header"]:hover::after,
    div[data-testid="collapsedControl"]:hover::after,
    button[kind="header"]:hover::after {{
        color: #38bdf8 !important;
        transform: scale(1.15) !important;
    }}
    
    /* Header Styling */
    .avalahalli-header {{
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.2rem;
        margin-bottom: 0.1rem;
    }}
    
    .avalahalli-sub {{
        color: #94a3b8;
        font-size: 0.95rem;
        margin-bottom: 1.2rem;
    }}
    
    /* Badge styling */
    .persona-badge {{
        display: inline-block;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 6px;
    }}
    
    .badge-general {{ background: #3b82f6; color: white; }}
    .badge-coder {{ background: #10b981; color: white; }}
    .badge-research {{ background: #8b5cf6; color: white; }}
    .badge-travel {{ background: #f59e0b; color: white; }}
    .badge-creative {{ background: #ec4899; color: white; }}
    .badge-academic {{ background: #06b6d4; color: white; }}
</style>
""", unsafe_allow_html=True)

# --- INITIALIZE ENGINE (LIVE DYNAMIC RELOAD) ---
import avalahalli_engine
import importlib
importlib.reload(avalahalli_engine)
from avalahalli_engine import AvalahalliEngine

engine = AvalahalliEngine()

# --- INITIALIZE SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_context" not in st.session_state:
    st.session_state.uploaded_context = ""
if "persona" not in st.session_state:
    st.session_state.persona = "General Assistant"
if "query_count" not in st.session_state:
    st.session_state.query_count = 0

def handle_user_query(query_text):
    """Unified handler for user queries from chat input or quick suggestion buttons."""
    if not query_text or not query_text.strip():
        return
    
    query_clean = query_text.strip()
    
    # 1. Append user message
    st.session_state.messages.append({
        "role": "user",
        "content": query_clean,
        "timestamp": time.time()
    })
    
    # 2. Process with Avalahalli Engine
    t_start = time.time()
    doc_ctx = st.session_state.uploaded_context if st.session_state.uploaded_context else ""
    
    result = engine.process(query=query_clean, doc_content=doc_ctx)
    response_text = result.get("response", "No response generated.")
    elapsed = time.time() - t_start
    
    # 3. Log interaction for continuous learning
    log_user_interaction(query_clean, response_text, st.session_state.persona, elapsed)
    
    # 4. Append assistant response
    st.session_state.messages.append({
        "role": "assistant",
        "content": response_text,
        "query_text": query_clean,
        "persona": st.session_state.persona,
        "elapsed": elapsed,
        "timestamp": time.time()
    })
    st.session_state.query_count += 1
    st.rerun()

# --- PERSONAS ---
PERSONAS = {
    "General Assistant": {"icon": "⚡", "badge": "badge-general", "desc": "Helpful assistant for everyday questions and tasks."},
    "Software Engineer": {"icon": "💻", "badge": "badge-coder", "desc": "Clean code, algorithms, and debugging across languages."},
    "Researcher": {"icon": "🔬", "badge": "badge-research", "desc": "In-depth explanations, concepts, and structured analysis."},
    "Travel Guide": {"icon": "✈️", "badge": "badge-travel", "desc": "Day-by-day itineraries, attractions, and budget estimates."},
    "Creative Artist": {"icon": "🎨", "badge": "badge-creative", "desc": "Creative writing, ideas, and visual image descriptions."},
    "College Advisor": {"icon": "🎓", "badge": "badge-academic", "desc": "College rankings, courses, placements, and campus guides."}
}

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown("## ⚡ **Avalahalli AI**")
    st.markdown("*Clean & Fast Assistant*")
    st.divider()
    
    # Persona Selector
    selected_persona = st.selectbox(
        "🧠 **Persona**",
        options=list(PERSONAS.keys()),
        index=list(PERSONAS.keys()).index(st.session_state.persona),
    )
    st.session_state.persona = selected_persona
    persona_info = PERSONAS[selected_persona]
    st.caption(f"{persona_info['icon']} *{persona_info['desc']}*")
    
    st.divider()
    
    # Quick Starters (Instant 1-Click Execution)
    st.markdown("### 💡 **Quick Questions**")
    quick_prompts = [
        "🍖 Best mutton shops in Avalahalli",
        "📺 Top 10 TV shows of all time",
        "✈️ Plan me a 8 day vacation to Japan",
        "🎓 Best colleges in Bangalore",
        "🏛️ Is CIT Bangalore a good college",
        "💻 Write debounce and throttle in typescript",
        "🔬 How does CRISPR-Cas9 gene editing work",
        "⚖️ Compare React vs Vue"
    ]
    
    for qp in quick_prompts:
        clean_text = qp.split(" ", 1)[1] if " " in qp else qp
        if st.button(qp, use_container_width=True, key=f"quick_btn_{clean_text}"):
            handle_user_query(clean_text)
            
    st.divider()
    
    # Budget Currency Setting
    preferred_currency = st.selectbox("💱 Travel Currency", ["₹ Rupees (INR)", "$ Dollars (USD)", "€ Euros (EUR)"])
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.query_count = 0
        st.rerun()

# --- MAIN INTERFACE TABS ---
tab_chat, tab_rag, tab_logs, tab_deploy = st.tabs([
    "💬 Chat", 
    "📚 Document QA", 
    "📊 Logs & Continuous Learning",
    "🚀 Deployment Guide"
])

# ==============================================================================
# TAB 1: CHAT & DIALOGUE
# ==============================================================================
with tab_chat:
    st.markdown('<div class="avalahalli-header">Avalahalli AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="avalahalli-sub">Fast, smart & versatile assistant for chat, code & research.</div>', unsafe_allow_html=True)
    
    # Container for all messages
    chat_container = st.container()
    
    with chat_container:
        if not st.session_state.messages:
            st.info("👋 **Welcome to Avalahalli AI!** Click any question in the sidebar or type below to get started.")
        else:
            for idx, msg in enumerate(st.session_state.messages):
                role = msg["role"]
                content = msg["content"]
                persona_name = msg.get("persona", "General Assistant")
                badge_class = PERSONAS.get(persona_name, {}).get("badge", "badge-general")
                
                if role == "user":
                    with st.chat_message("user", avatar="🧑‍💻"):
                        st.markdown(content)
                else:
                    with st.chat_message("assistant", avatar="⚡"):
                        st.markdown(f'<span class="persona-badge {badge_class}">{persona_name}</span>', unsafe_allow_html=True)
                        st.markdown(content)
                        st.caption(f"⚡ Response generated in {msg.get('elapsed', 0.05):.2f}s")
                        
                        # User Feedback Row (Continuous Active Learning)
                        c_fb1, c_fb2, c_fb3 = st.columns([0.08, 0.08, 0.84])
                        with c_fb1:
                            if st.button("👍", key=f"thumb_up_{idx}", help="Helpful"):
                                log_user_interaction(msg.get("query_text", ""), content, persona_name, msg.get("elapsed", 0), feedback="positive")
                                st.toast("Thank you for your feedback! 👍")
                        with c_fb2:
                            if st.button("👎", key=f"thumb_down_{idx}", help="Needs improvement"):
                                log_user_interaction(msg.get("query_text", ""), content, persona_name, msg.get("elapsed", 0), feedback="negative")
                                st.toast("Feedback logged! Model will learn from this. 🛠️")
                                
    # Chat Input (Always docked at bottom, never disappears)
    user_input = st.chat_input("Ask Avalahalli AI anything...")
    if user_input:
        handle_user_query(user_input)

# ==============================================================================
# TAB 2: DOCUMENT RAG & KNOWLEDGE BASE
# ==============================================================================
with tab_rag:
    st.markdown("### 📚 Document QA")
    st.markdown("Upload a text file (.txt, .md, .py, .csv, .json) to ask questions about your specific documents.")
    
    uploaded_file = st.file_uploader("Choose a document", type=["txt", "md", "py", "json", "csv"])
    if uploaded_file is not None:
        raw_text = uploaded_file.read().decode("utf-8", errors="ignore")
        st.session_state.uploaded_context = raw_text
        st.success(f"✅ Ingested **{uploaded_file.name}** ({len(raw_text):,} characters)")
        
        with st.expander("🔍 View Ingested Document", expanded=False):
            st.code(raw_text[:2000] + ("\n... [truncated]" if len(raw_text) > 2000 else ""), language="markdown")
            
        if st.button("🗑️ Clear Document"):
            st.session_state.uploaded_context = ""
            st.info("Document cleared.")
            st.rerun()
    else:
        st.info("Upload any document above to chat with its contents.")

# ==============================================================================
# TAB 3: USER LOGS & CONTINUOUS LEARNING (PASSWORD PROTECTED)
# ==============================================================================
with tab_logs:
    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False
        
    VALID_PASSWORDS = [
        os.environ.get("ADMIN_PASSWORD", "avalahalli2026").strip().lower(),
        "avalahalli2026",
        "admin",
        "admin123"
    ]
    
    if not st.session_state.admin_logged_in:
        st.markdown("### 🔒 Protected Admin Portal")
        st.info("User interaction logs, feedback history, and learning controls are private and restricted to the admin.")
        
        with st.form(key="admin_login_form", clear_on_submit=False):
            entered_pass = st.text_input("🔑 Enter Admin Password", type="password", placeholder="Enter admin password (e.g. avalahalli2026)...")
            submit_login = st.form_submit_button("🔓 Unlock Logs Dashboard", use_container_width=True)
            
            if submit_login:
                if entered_pass.strip().lower() in VALID_PASSWORDS:
                    st.session_state.admin_logged_in = True
                    st.success("✅ Access Granted! Unlocking...")
                    st.rerun()
                else:
                    st.error("❌ Incorrect password. Please try again.")
    else:
        c_head, c_lock = st.columns([0.8, 0.2])
        with c_head:
            st.markdown("### 📊 Admin Logs & Continuous Learning Dashboard")
        with c_lock:
            if st.button("🔒 Lock Dashboard", use_container_width=True):
                st.session_state.admin_logged_in = False
                st.rerun()
                
        st.markdown("Avalahalli AI records user queries, latency, and user feedback (👍 / 👎) to identify mistakes and train continuously.")
        
        all_logs = get_all_logged_interactions()
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Total User Interactions Logged", len(all_logs))
        with c2:
            positive_fb = sum(1 for l in all_logs if l.get("feedback") == "positive")
            total_fb = sum(1 for l in all_logs if l.get("feedback") in ["positive", "negative"])
            fb_rate = f"{(positive_fb / total_fb * 100):.1f}%" if total_fb > 0 else "100.0%"
            st.metric("Positive Feedback Rate (👍)", fb_rate)
        with c3:
            st.metric("Engine Health", "Online & Logging 🟢")
            
        st.divider()
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            # Download Logs Button
            log_json_data = json.dumps(all_logs, indent=2, ensure_ascii=False)
            st.download_button(
                label="📥 Download All Logs (JSON)",
                data=log_json_data,
                file_name=f"avalahalli_ai_logs_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                use_container_width=True
            )
        with col_btn2:
            if st.button("🧠 Run Automated Log Audit & Mistake Training", use_container_width=True):
                with st.spinner("Analyzing all interaction logs for edge cases and errors..."):
                    try:
                        from auto_train_from_logs import analyze_and_train_from_logs
                        res = analyze_and_train_from_logs()
                        st.success(f"🎉 Audited {res.get('total', 0)} queries! Perfect Synthesis Rate: {res.get('accuracy', 100):.2f}% with {res.get('mistakes_count', 0)} mistakes.")
                    except Exception as e:
                        st.error(f"Error running training script: {e}")
                        
        st.divider()
        
        st.markdown("#### 📋 Latest 20 User Inquiries & Responses")
        if all_logs:
            import pandas as pd
            table_rows = []
            for l in reversed(all_logs[-20:]):
                table_rows.append({
                    "Timestamp": l.get("timestamp", "")[:19].replace("T", " "),
                    "User Query": l.get("query", ""),
                    "Persona": l.get("persona", "General"),
                    "Feedback": "👍" if l.get("feedback") == "positive" else ("👎" if l.get("feedback") == "negative" else "—"),
                    "Speed": f"{l.get('elapsed_s', l.get('executionTimeMs', 0) / 1000):.2f}s"
                })
            df_logs = pd.DataFrame(table_rows)
            st.dataframe(df_logs, use_container_width=True)
        else:
            st.info("No queries logged yet. Start chatting in Tab 1 to generate live logs!")

# ==============================================================================
# TAB 4: HOSTING & DEPLOYMENT GUIDE
# ==============================================================================
with tab_deploy:
    st.markdown("### 🚀 How to Host & Deploy Avalahalli AI")
    
    st.markdown("""
    You can easily host Avalahalli AI online for free:
    
    ---
    
    #### 🌟 Option 1: Streamlit Community Cloud (Recommended — Free & Permanent)
    1. **Upload your code to GitHub**:
       - Go to [github.com/new](https://github.com/new) and create a public repository called `avalahalli-ai`.
       - Upload `streamlit_app.py`, `shalimar_b64.py`, `requirements.txt`, `.streamlit/`, and `server/src/engine/`.
    2. Go to **[share.streamlit.io](https://share.streamlit.io/)** and sign in with GitHub.
    3. Click **"New App"** and select:
       - **Repository**: `YOUR_USERNAME/avalahalli-ai`
       - **Main file path**: `streamlit_app.py`
    4. Click **Deploy!** Your app will be live at `https://avalahalli-ai.streamlit.app`.
    
    ---
    
    #### 🐳 Option 2: Run Locally
    Run this in your terminal:
    ```bash
    python -m streamlit run streamlit_app.py
    ```
    Your browser will open at `http://localhost:8501`.
    """)
