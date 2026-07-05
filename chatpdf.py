import hashlib
from io import BytesIO
from html import escape

import requests
import streamlit as st
from PyPDF2 import PdfReader

st.set_page_config(
    page_title="AI PDF Chat",
    layout="wide",
    initial_sidebar_state="expanded"
)

BACKEND_URL = "http://127.0.0.1:8000/pdf_query"

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(59, 130, 246, 0.16), transparent 34%),
            radial-gradient(circle at bottom right, rgba(168, 85, 247, 0.14), transparent 35%),
            #070b14;
        color: #e5e7eb;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1250px;
    }

    section[data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.94);
        border-right: 1px solid rgba(148, 163, 184, 0.14);
    }

    .hero-card {
        padding: 34px 36px;
        border-radius: 24px;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.96), rgba(30, 41, 59, 0.86));
        border: 1px solid rgba(148, 163, 184, 0.18);
        box-shadow: 0 24px 70px rgba(0, 0, 0, 0.38);
        margin-bottom: 26px;
    }

    .hero-title {
        font-size: 44px;
        line-height: 1.05;
        font-weight: 900;
        letter-spacing: -1.3px;
        margin-bottom: 12px;
        background: linear-gradient(135deg, #60a5fa, #a78bfa, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-subtitle {
        font-size: 16px;
        color: #94a3b8;
        max-width: 760px;
        line-height: 1.7;
    }

    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        border-radius: 999px;
        background: rgba(34, 197, 94, 0.11);
        border: 1px solid rgba(34, 197, 94, 0.24);
        color: #86efac;
        font-size: 13px;
        font-weight: 700;
        margin-bottom: 18px;
    }

    .empty-card {
        padding: 42px 34px;
        border-radius: 22px;
        background: rgba(15, 23, 42, 0.72);
        border: 1px dashed rgba(148, 163, 184, 0.28);
        text-align: center;
        color: #94a3b8;
    }

    .empty-card h3 {
        color: #f8fafc;
        font-size: 24px;
        margin-bottom: 8px;
    }

    .metric-card {
        padding: 18px;
        border-radius: 18px;
        background: rgba(15, 23, 42, 0.82);
        border: 1px solid rgba(148, 163, 184, 0.16);
        text-align: center;
    }

    .metric-value {
        font-size: 28px;
        font-weight: 900;
        color: #60a5fa;
    }

    .metric-label {
        font-size: 12px;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 4px;
    }

    .sidebar-title {
        font-size: 22px;
        font-weight: 900;
        color: #f8fafc;
        margin-bottom: 6px;
    }

    .sidebar-caption {
        color: #94a3b8;
        font-size: 14px;
        line-height: 1.6;
        margin-bottom: 18px;
    }

    .file-name-box {
        padding: 14px 16px;
        border-radius: 14px;
        background: rgba(30, 41, 59, 0.78);
        border: 1px solid rgba(148, 163, 184, 0.18);
        color: #e2e8f0;
        font-size: 14px;
        margin-top: 14px;
        word-break: break-word;
    }

    div[data-testid="stFileUploader"] {
        padding: 16px;
        border-radius: 18px;
        background: rgba(30, 41, 59, 0.58);
        border: 1px solid rgba(148, 163, 184, 0.16);
    }

    div[data-testid="stChatMessage"] {
        border-radius: 20px;
        padding: 16px 18px;
        margin-bottom: 14px;
        border: 1px solid rgba(148, 163, 184, 0.13);
        background: rgba(15, 23, 42, 0.70);
    }

    textarea[data-testid="stChatInputTextArea"] {
        background: rgba(15, 23, 42, 0.95) !important;
        color: #f8fafc !important;
        border: 1px solid rgba(148, 163, 184, 0.24) !important;
        border-radius: 16px !important;
    }

    .stButton > button {
        width: 100%;
        border-radius: 14px;
        border: 1px solid rgba(96, 165, 250, 0.24);
        background: rgba(30, 41, 59, 0.72);
        color: #e5e7eb;
        font-weight: 700;
        padding: 12px 16px;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        background: rgba(37, 99, 235, 0.26);
        border-color: rgba(96, 165, 250, 0.5);
        color: #ffffff;
    }

    .stAlert {
        border-radius: 16px;
    }
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "active_pdf_hash" not in st.session_state:
    st.session_state.active_pdf_hash = None

if "queued_question" not in st.session_state:
    st.session_state.queued_question = None

@st.cache_data(show_spinner=False)
def extract_pdf_text(file_bytes):
    reader = PdfReader(BytesIO(file_bytes))
    text = ""
    total_pages = len(reader.pages)

    for page in reader.pages:
        text += page.extract_text() or ""

    return text.strip(), total_pages

def get_file_hash(file_bytes):
    return hashlib.md5(file_bytes).hexdigest()

def ask_backend(pdf_text, question):
    response = requests.post(
        BACKEND_URL,
        json={
            "text": pdf_text,
            "question": question
        },
        timeout=120
    )

    response.raise_for_status()
    data = response.json()

    return data.get("result", "No answer returned from backend.")

with st.sidebar:
    st.markdown('<div class="sidebar-title">AI PDF Chat</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sidebar-caption">Upload a PDF and ask questions from its content using your FastAPI backend.</div>',
        unsafe_allow_html=True
    )

    uploaded_pdf = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        label_visibility="collapsed"
    )

    st.divider()

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("### Backend")
    st.code(BACKEND_URL, language="text")

pdf_text = ""
total_pages = 0
total_chars = 0
estimated_tokens = 0
pdf_ready = False

if uploaded_pdf is not None:
    file_bytes = uploaded_pdf.getvalue()
    current_hash = get_file_hash(file_bytes)

    if st.session_state.active_pdf_hash != current_hash:
        st.session_state.active_pdf_hash = current_hash
        st.session_state.messages = []

    try:
        pdf_text, total_pages = extract_pdf_text(file_bytes)
        total_chars = len(pdf_text)
        estimated_tokens = total_chars // 4
        pdf_ready = bool(pdf_text)

    except Exception as e:
        st.error(f"Could not read PDF: {e}")

st.markdown("""
<div class="hero-card">
    <div class="status-pill">PDF Intelligence Workspace</div>
    <div class="hero-title">Chat with your PDF beautifully.</div>
    <div class="hero-subtitle">
        Upload your document, extract its text, and ask questions through your AI backend.
        Built for clean reading, faster interaction, and a better project presentation.
    </div>
</div>
""", unsafe_allow_html=True)

if uploaded_pdf is not None and pdf_ready:
    safe_file_name = escape(uploaded_pdf.name)

    st.markdown(
        f"""
        <div class="file-name-box">
            <b>Active document:</b> {safe_file_name}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    metric_col1, metric_col2, metric_col3 = st.columns(3)

    with metric_col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{total_pages}</div>
                <div class="metric-label">Pages</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with metric_col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{estimated_tokens}</div>
                <div class="metric-label">Estimated Tokens</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with metric_col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{total_chars}</div>
                <div class="metric-label">Characters</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")
    st.write("")

    if not st.session_state.messages:
        st.markdown("""
        <div class="empty-card">
            <h3>Ready to analyze your PDF</h3>
            <p>Ask for a summary, key points, definitions, conclusions, or anything inside the document.</p>
        </div>
        """, unsafe_allow_html=True)

        st.write("")

        q1, q2, q3 = st.columns(3)

        with q1:
            if st.button("Summarize this PDF"):
                st.session_state.queued_question = "Summarize this PDF in simple points."

        with q2:
            if st.button("Give key points"):
                st.session_state.queued_question = "What are the key points in this PDF?"

        with q3:
            if st.button("Explain simply"):
                st.session_state.queued_question = "Explain this PDF in simple beginner-friendly language."

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    typed_question = st.chat_input("Ask anything about your PDF...")

    if st.session_state.queued_question:
        user_question = st.session_state.queued_question
        st.session_state.queued_question = None
    else:
        user_question = typed_question

    if user_question:
        st.session_state.messages.append({
            "role": "user",
            "content": user_question
        })

        with st.chat_message("user"):
            st.markdown(user_question)

        with st.chat_message("assistant"):
            with st.spinner("Reading your PDF and generating answer..."):
                try:
                    answer = ask_backend(pdf_text, user_question)
                    st.markdown(answer)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer
                    })

                except requests.exceptions.ConnectionError:
                    error_msg = "Could not connect to backend. Run FastAPI backend first using: uvicorn backend:app --reload"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })

                except requests.exceptions.Timeout:
                    error_msg = "Backend took too long to respond. Try again with a smaller PDF."
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })

                except requests.exceptions.HTTPError as e:
                    error_msg = f"Backend returned an error: {e}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })

                except Exception as e:
                    error_msg = f"Something went wrong: {e}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })

else:
    st.markdown("""
    <div class="empty-card">
        <h3>Upload a PDF to begin</h3>
        <p>Your document panel is in the sidebar. Upload a PDF, then the chat workspace will unlock.</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    st.info("Run your FastAPI backend first: uvicorn backend:app --reload")