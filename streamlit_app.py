"""
================================================================================
⚡ AVALAHALLI AI (STREAMLIT HUB)
Clean, fast, and versatile AI assistant for chat, coding, and research.
================================================================================
"""

import streamlit as st
import time
import json
import os
import sys
import re
import base64

# Add engine path
ENGINE_DIR = os.path.join(os.path.dirname(__file__), 'server', 'src', 'engine')
if ENGINE_DIR not in sys.path:
    sys.path.insert(0, ENGINE_DIR)

try:
    from avalahalli_engine import AvalahalliEngine
except ImportError:
    st.error(f"Could not import AvalahalliEngine from {ENGINE_DIR}. Please check the directory path.")
    st.stop()

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

    .main .block-container {{
        position: relative;
        z-index: 1;
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
    
    # Quick Starters
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
        if st.button(qp, use_container_width=True):
            st.session_state.prefill_prompt = qp.split(" ", 1)[1]
            st.rerun()
            
    st.divider()
    
    # Budget Currency Setting
    preferred_currency = st.selectbox("💱 Travel Currency", ["₹ Rupees (INR)", "$ Dollars (USD)", "€ Euros (EUR)"])
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.query_count = 0
        st.rerun()

# --- MAIN INTERFACE TABS ---
tab_chat, tab_rag, tab_deploy = st.tabs([
    "💬 Chat", 
    "📚 Document QA", 
    "🚀 Deployment Guide"
])

# ==============================================================================
# TAB 1: CHAT & DIALOGUE
# ==============================================================================
with tab_chat:
    st.markdown('<div class="avalahalli-header">Avalahalli AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="avalahalli-sub">Fast, smart & versatile assistant for chat, code & research.</div>', unsafe_allow_html=True)
    
    # Display message history
    if not st.session_state.messages:
        st.info("👋 **Welcome to Avalahalli AI!** Type a question below or choose a suggestion from the sidebar to get started.")
    else:
        for msg in st.session_state.messages:
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
                    
    # Chat Input Box
    default_prompt = st.session_state.pop("prefill_prompt", "")
    user_input = st.chat_input("Ask Avalahalli AI anything...") or default_prompt
    
    if user_input:
        # Add user message to history
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": time.time()
        })
        
        # Display user message immediately
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(user_input)
            
        # Process with Avalahalli Engine
        with st.chat_message("assistant", avatar="⚡"):
            badge_class = PERSONAS[st.session_state.persona]["badge"]
            st.markdown(f'<span class="persona-badge {badge_class}">{st.session_state.persona}</span>', unsafe_allow_html=True)
            
            with st.spinner("Generating response..."):
                t_start = time.time()
                
                # Context injection if document uploaded
                doc_ctx = st.session_state.uploaded_context if st.session_state.uploaded_context else ""
                
                # Format query with currency if requested
                effective_query = user_input
                if "Rupees" in preferred_currency and not any(w in user_input.lower() for w in ["rupee", "rupees", "inr", "₹"]):
                    if any(w in user_input.lower() for w in ["travel", "trip", "vacation", "pricing", "budget", "cost", "hotel"]):
                        effective_query += " in rupees"
                
                # Execute engine
                result = engine.process(
                    query=effective_query,
                    doc_content=doc_ctx
                )
                
                response_text = result.get("response", "No response generated.")
                elapsed = time.time() - t_start
                
                # Render response
                st.markdown(response_text)
                st.caption(f"⚡ Response generated in {elapsed:.2f}s")
                
                # Record to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text,
                    "persona": st.session_state.persona,
                    "elapsed": elapsed,
                    "timestamp": time.time()
                })
                st.session_state.query_count += 1

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
# TAB 3: HOSTING & DEPLOYMENT GUIDE
# ==============================================================================
with tab_deploy:
    st.markdown("### 🚀 How to Host & Deploy Avalahalli AI")
    
    st.markdown("""
    You can easily host Avalahalli AI online for free:
    
    ---
    
    #### 🌟 Option 1: Streamlit Community Cloud (Recommended — Free & Permanent)
    1. **Upload your code to GitHub**:
       - Go to [github.com/new](https://github.com/new) and create a public repository called `avalahalli-ai`.
       - Upload `streamlit_app.py`, `requirements.txt`, `.streamlit/`, and `server/src/engine/`.
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
