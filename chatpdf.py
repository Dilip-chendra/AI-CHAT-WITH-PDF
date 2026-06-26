import streamlit as st
import requests
from PyPDF2 import PdfReader

st.set_page_config(page_title="ChatToPDF Pro", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f111a 0%, #15192e 100%) !important;
        color: #e2e8f0 !important;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 16px !important;
        padding: 24px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
    }
    .metric-box {
        text-align: center;
        padding: 15px;
        background: rgba(255, 255, 255, 0.01);
        border-radius: 12px;
        border-left: 4px solid #6366f1;
    }
    .metric-val {
        font-size: 24px;
        font-weight: 700;
        color: #6366f1;
    }
    .metric-lbl {
        font-size: 12px;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 5px;
    }
    .chat-bubble {
        padding: 16px 20px;
        border-radius: 14px;
        margin-bottom: 12px;
        line-height: 1.6;
        font-size: 15px;
    }
    .user-bubble {
        background: rgba(99, 102, 241, 0.15) !important;
        border-left: 4px solid #6366f1 !important;
        margin-left: 20%;
    }
    .ai-bubble {
        background: rgba(16, 185, 129, 0.1) !important;
        border-left: 4px solid #10b981 !important;
        margin-right: 20%;
    }
    .bubble-header {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 6px;
        font-weight: 600;
    }
    div.stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.04) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        padding: 12px !important;
    }
    div.stTextInput > div > div > input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 10px rgba(99, 102, 241, 0.4) !important;
    }
    </style>
""", unsafe_allow_html=True)

if "pdf_chat_history" not in st.session_state:
    st.session_state.pdf_chat_history = []

left_panel, right_panel = st.columns([1, 2], gap="large")

with left_panel:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## ⚡ **Neural PDF Workspace**")
    st.markdown("<p style='color:#94a3b8;'>Upload documentation models to compute context vector search matrices.</p>", unsafe_allow_html=True)
    
    pdf = st.file_uploader("Ingest Document Data Engine", type="pdf", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if pdf is not None:
        pdf_reader = PdfReader(pdf)
        total_pages = len(pdf_reader.pages)
        raw_text = ""
        for page in pdf_reader.pages:
            raw_text += page.extract_text() or ""
        total_chars = len(raw_text)
        estimated_tokens = int(total_chars / 4)
        
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 📊 **Vector Extraction Metrics**")
        st.markdown("<br>", unsafe_allow_html=True)
        
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.markdown(f'<div class="metric-box"><div class="metric-val">{total_pages}</div><div class="metric-lbl">Total Pages</div></div>', unsafe_allow_html=True)
        with m_col2:
            st.markdown(f'<div class="metric-box"><div class="metric-val">{estimated_tokens}</div><div class="metric-lbl">Est. Tokens</div></div>', unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="glass-card" style="text-align:center; padding:40px !important; color:#64748b;">🔄 Awaiting document ingestion matrix initialization.</div>', unsafe_allow_html=True)

with right_panel:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("<h1>🧠 :rainbow[Cognitive Query Space]</h1>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    for chat in st.session_state.pdf_chat_history:
        if chat["role"] == "user":
            st.markdown(f'''
                <div class="chat-bubble user-bubble">
                    <div class="bubble-header" style="color:#a5b4fc;">👤 Human Investigator</div>
                    {chat["content"]}
                </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown(f'''
                <div class="chat-bubble ai-bubble">
                    <div class="bubble-header" style="color:#6ee7b7;">🤖 LangChain Core Engine</div>
                    {chat["content"]}
                </div>
            ''', unsafe_allow_html=True)
            
    if pdf is not None:
        user_question = st.text_input("Interrogate Context Memory Engine:", placeholder="Ask a targeted question about the ingested PDF document...")
        
        if st.button("Execute Vector Query Execution") and user_question.strip():
            st.session_state.pdf_chat_history.append({"role": "user", "content": user_question})
            st.rerun()

if pdf is not None and "pdf_chat_history" in st.session_state and len(st.session_state.pdf_chat_history) > 0:
    if st.session_state.pdf_chat_history[-1]["role"] == "user":
        with right_panel:
            with st.spinner("Computing document similarity vectors..."):
                try:
                    backend_url = "https://onrender.com"
                    pdf_reader = PdfReader(pdf)
                    text_payload = ""
                    for page in pdf_reader.pages:
                        text_payload += page.extract_text() or ""
                        
                    post_data = {
                        "text": text_payload,
                        "question": st.session_state.pdf_chat_history[-1]["content"]
                    }
                    
                    response = requests.post(url=backend_url, json=post_data)
                    
                    if response.status_code == 200:
                        data = response.json()
                        ai_final_text = data["result"]
                        st.session_state.pdf_chat_history.append({"role": "assistant", "content": ai_final_text})
                        st.rerun()
                    else:
                        st.error(f"Neural Node Connection Aborted (Status Code {response.status_code})")
                except Exception as e:
                    st.error(f"Critical Gateway Synchronization Disruption: {e}")
