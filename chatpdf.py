import streamlit as st
import requests
from PyPDF2 import PdfReader

st.set_page_config(page_title="PDF Intelligence Workspace", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-color: #0b0d17 !important;
        background-image: radial-gradient(at 0% 0%, rgba(30, 41, 59, 0.3) 0, transparent 50%), 
                          radial-gradient(at 100% 100%, rgba(15, 23, 42, 0.3) 0, transparent 50%) !important;
        color: #f8fafc !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    .panel-card {
        background: #111424 !important;
        border: 1px solid #1e293b !important;
        border-radius: 12px !important;
        padding: 28px !important;
        margin-bottom: 24px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4) !important;
    }
    
    .gradient-header {
        font-size: 38px !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px !important;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        margin-bottom: 8px !important;
        line-height: 1.2 !important;
    }
    
    .section-title {
        font-size: 20px !important;
        font-weight: 700 !important;
        color: #f1f5f9 !important;
        letter-spacing: -0.3px !important;
        margin-bottom: 6px !important;
        border-left: 3px solid #38bdf8;
        padding-left: 12px !important;
    }
    
    .metric-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
        margin-top: 20px;
    }
    
    .metric-tile {
        background: #161b33 !important;
        border: 1px solid rgba(56, 189, 248, 0.1) !important;
        border-radius: 8px !important;
        padding: 18px 14px !important;
        text-align: center;
    }
    
    .metric-value {
        font-size: 26px !important;
        font-weight: 700 !important;
        color: #38bdf8 !important;
        line-height: 1 !important;
    }
    
    .metric-label {
        font-size: 11px !important;
        color: #64748b !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
        margin-top: 6px !important;
        font-weight: 600 !important;
    }
    
    .status-alert {
        text-align: center;
        padding: 32px 20px !important;
        background: #141729 !important;
        border: 1px dashed #334155 !important;
        border-radius: 8px !important;
        color: #64748b !important;
        font-size: 14px !important;
    }
    
    .bubble-wrapper {
        margin-bottom: 18px !important;
        max-width: 85%;
    }
    
    .bubble-wrapper.user-side {
        margin-left: auto;
    }
    
    .bubble-meta {
        font-size: 10px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        margin-bottom: 4px !important;
    }
    
    .custom-bubble {
        padding: 16px 20px !important;
        border-radius: 12px !important;
        font-size: 15px !important;
        line-height: 1.6 !important;
    }
    
    .user-side .custom-bubble {
        background: #1e1b4b !important;
        border: 1px solid #3730a3 !important;
        color: #e0e7ff !important;
    }
    
    .ai-side .custom-bubble {
        background: #064e3b !important;
        border: 1px solid #065f46 !important;
        color: #ecfdf5 !important;
    }
    
    div.stTextInput > div > div > input {
        background: #111424 !important;
        color: #ffffff !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        padding: 14px !important;
        font-size: 15px !important;
    }
    
    div.stTextInput > div > div > input:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 1px #38bdf8 !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #38bdf8 0%, #6366f1 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        letter-spacing: 0.3px !important;
        transition: opacity 0.2s ease !important;
    }
    
    .stButton > button:hover {
        opacity: 0.9 !important;
    }
    </style>
""", unsafe_allow_html=True)

if "pdf_chat_history" not in st.session_state:
    st.session_state.pdf_chat_history = []

left_panel, right_panel = st.columns([1, 2], gap="large")

with left_panel:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Document Ingestion</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#64748b; font-size:14px; margin-top:8px; margin-bottom:16px;">Upload a source documentation asset to compute contextual search mappings.</p>', unsafe_allow_html=True)
    
    pdf = st.file_uploader("Upload PDF file", type="pdf", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if pdf is not None:
        pdf_reader = PdfReader(pdf)
        total_pages = len(pdf_reader.pages)
        raw_text = ""
        for page in pdf_reader.pages:
            raw_text += page.extract_text() or ""
        total_chars = len(raw_text)
        estimated_tokens = int(total_chars / 4)
        
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Analysis Metrics</div>', unsafe_allow_html=True)
        
        st.markdown(f'''
            <div class="metric-container">
                <div class="metric-tile">
                    <div class="metric-value">{total_pages}</div>
                    <div class="metric-label">Total Pages</div>
                </div>
                <div class="metric-tile">
                    <div class="metric-value">{estimated_tokens}</div>
                    <div class="metric-label">Est Tokens</div>
                </div>
            </div>
        ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-alert">Awaiting file upload session initialization.</div>', unsafe_allow_html=True)

with right_panel:
    st.markdown('<h1 class="gradient-header">Cognitive Query Space</h1>', unsafe_allow_html=True)
    st.markdown('<hr style="border:0; height:1px; background:#1e293b; margin-bottom:24px;">', unsafe_allow_html=True)
    
    for chat in st.session_state.pdf_chat_history:
        if chat["role"] == "user":
            st.markdown(f'''
                <div class="bubble-wrapper user-side">
                    <div class="bubble-meta" style="color:#818cf8; text-align:right;">Human Investigator</div>
                    <div class="custom-bubble">{chat["content"]}</div>
                </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown(f'''
                <div class="bubble-wrapper ai-side">
                    <div class="bubble-meta" style="color:#34d399;">Core Analysis Engine</div>
                    <div class="custom-bubble">{chat["content"]}</div>
                </div>
            ''', unsafe_allow_html=True)
            
    if pdf is not None:
        st.markdown('<br>', unsafe_allow_html=True)
        user_question = st.text_input("Query Input", placeholder="Submit an interrogation request about the document content...", label_visibility="collapsed")
        
        if st.button("Execute Vector Query") and user_question.strip():
            st.session_state.pdf_chat_history.append({"role": "user", "content": user_question})
            st.rerun()

if pdf is not None and "pdf_chat_history" in st.session_state and len(st.session_state.pdf_chat_history) > 0:
    if st.session_state.pdf_chat_history[-1]["role"] == "user":
        with right_panel:
            with st.spinner("Computing document similarity arrays..."):
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
                        st.error(f"Network node communication failure (Status Code {response.status_code})")
                except Exception as e:
                    st.error(f"Gateway synchronization disruption: {e}")
