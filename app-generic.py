'''
This code is the rewrite of the original app.py (currently called app.py.bak) to set up generic function call to the LLM.
The idea was to isolate the generic LLM call in a single function for easier future modifications.
'''






import streamlit as st
import requests
import json
from io import BytesIO

import logging
import os
os.makedirs("/tmp", exist_ok=True)
logging.basicConfig(filename='/tmp/streamlit.log', level=logging.INFO)

# PDF/DOCX imports with fallbacks
try:
    import pypdf as pdf_lib
    PDF_AVAILABLE = True
except ImportError:
    try:
        import PyPDF2 as pdf_lib
        PDF_AVAILABLE = True
    except ImportError:
        PDF_AVAILABLE = False

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "gemma3:1b"  # make sure this matches the model name you pulled
TIMEOUT_SECONDS = 60
max_size_mb = 2

# ---- Initialize session state (CRITICAL - prevents AttributeError) ----
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! Paste your resume or upload a file, then ask questions about it."}]

if "file_context" not in st.session_state:
    st.session_state.file_context = ""

if "current_file" not in st.session_state:
    st.session_state.current_file = None

# ---- File processing functions ----
try:
    import pypdf  # Newer, more reliable PDF library
    PDF_LIB = "pypdf"
except ImportError:
    import PyPDF2
    PDF_LIB = "PyPDF2"

def extract_text_from_file(uploaded_file):
    """Extract text from PDF, DOCX, or TXT file."""
    file_value = uploaded_file.getvalue()
    
    if "pdf" in uploaded_file.type:
        if PDF_LIB == "pypdf":
            pdf_reader = pypdf.PdfReader(BytesIO(file_value))
            text = " ".join(page.extract_text() or "" for page in pdf_reader.pages)
        else:
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_value))
            text = " ".join(page.extract_text() or "" for page in pdf_reader.pages)
    elif "docx" in uploaded_file.type:
        doc = docx.Document(BytesIO(file_value))
        text = " ".join(para.text for para in doc.paragraphs)
    elif uploaded_file.type == "text/plain":
        text = file_value.decode('utf-8')
    else:
        return None
    
    return text[:8000]  # Truncate to reasonable size


# ---- GenAI (local instance of Ollama) call ----
def call_ollama_gemma(prompt_text: str, file_context: str = "") -> str:
    """
    Send the prompt to a local Ollama instance (Gemma 3 1B) with optional file context.
    """
    if file_context:
        system_prompt = f"""You are a helpful assistant. Use the following document context to inform your response:
        
        CONTEXT FROM UPLOADED FILE:
        {file_context}
        
        Answer questions based primarily on this document context, and supplement with your general knowledge only when necessary."""
    else:
        system_prompt = "You are a helpful assistant."
    
    payload = {
        "model": OLLAMA_MODEL,
        "stream": False,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt_text},
        ],
    }

    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT_SECONDS)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"Error calling local Ollama: {e}"

    try:
        data = resp.json()
    except json.JSONDecodeError:
        return "Error: could not decode response from Ollama."

    message = data.get("message") or {}
    content = message.get("content")
    if not content:
        return "Error: Ollama returned an empty response."

    return content
    
# ---- End GenAI call ----

#---Placeholder for GenAI call ----
def call_genai_api(prompt_text: str) -> str:
    # TODO: implement your model call
    return f"(Echo) You said: {prompt_text[:200]}"

#---End Placeholder for GenAI call ----



st.set_page_config(
    page_title="My GenAI Chat",
    page_icon="💬",
    layout="wide",
)

st.markdown(
    """
    <style>
    .chat-bubble-user {
        background-color: #365972;
        padding: 0.75rem 1rem;
        border-radius: 1rem;
        margin: 0.25rem 0;
        max-width: 80%;
        margin-left: auto;
        color: #FFFFFF;
    }
    .chat-bubble-assistant {
        background-color: #787878;
        padding: 0.75rem 1rem;
        border-radius: 1rem;
        margin: 0.25rem 0;
        max-width: 80%;
        color: #FFFFFF;
    }
    .center-button button {
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---- Initialize state ----
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! Ask me anything."}
    ]

# ---- Page layout ----
left_col, center_col, right_col = st.columns([1, 2, 1])

with center_col:
    st.markdown(
        """
        <h2 style="text-align:center; margin-bottom:0.25rem;">My Resume-Job Matching Companion</h2>
        <p style="text-align:center; color:gray; margin-top:0;">Built by AI from Scratch Project 5</p>
        """,
        unsafe_allow_html=True,
    )

    # Chat container
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(
                    f"""
                    <div class="chat-bubble-user">
                        <strong>You</strong><br>{msg["content"]}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div class="chat-bubble-assistant">
                        <strong>Assistant</strong><br>{msg["content"]}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )



# Replace the entire form + submission section with this:

    # ---- Input area in CENTER column ----
    with st.form(key="chat_form", clear_on_submit=True):
        # Text prompt (centered column)
        prompt = st.text_area(
            "Ask a question or add context about your resume and/or the role you seek:",
            height=100,
            placeholder="What skills do I have? What experience matches this job? ...",
        )

#        st.markdown(
#            "**Attach resume file (PDF / DOCX / TXT)**  \n"
#            "_NOTE: There is a limit of 2MB per file_"
#        )
        uploaded_file = st.file_uploader(
            "file_uploader_internal_label",
            type=["pdf", "docx", "txt"],
            label_visibility="collapsed",
        )

        if uploaded_file is not None:
            file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
            if file_size_mb > max_size_mb:
                st.error(
                    f"File too large: {file_size_mb:.2f} MB "
                    f"(limit is {max_size_mb} MB)"
                )
                uploaded_file = None
            else:
                st.caption(f"Uploaded: {uploaded_file.name} ({file_size_mb:.2f} MB)")

        submitted = st.form_submit_button("Send")

    # ---- Submission handling (prompt + file synchronous) ----
    if submitted and prompt.strip():
        # Extract context from the file *for this question*
        file_context = ""
        if uploaded_file is not None:
            file_text = extract_text_from_file(uploaded_file)
            if file_text:
                file_context = file_text
                # Optional: persist latest file in session_state
                st.session_state.file_context = file_text
                st.session_state.current_file = uploaded_file
            else:
                st.error("Could not extract text from file; answering using your question only.")

        # 1) Append user message (note attached file)
        user_msg = prompt.strip()
        if uploaded_file is not None:
            user_msg += f"\n\n[Attached file: {uploaded_file.name}]"
        st.session_state.messages.append({"role": "user", "content": user_msg})

        # 2) Call Ollama with both question and (optional) file context
        with st.spinner("Thinking..."):
            response_text = call_ollama_gemma(prompt.strip(), file_context)

        # 3) Append assistant message
        st.session_state.messages.append(
            {"role": "assistant", "content": response_text}
        )

        # 4) Rerun to refresh the chat display
        st.rerun()
       
    # ---- End Submission handling ----

# ---- End Page layout ----

# ---- Install requirements ----
#st.sidebar.markdown("### 📦 Install packages")
#st.sidebar.code("""pip install PyPDF2 python-docx requests streamlit""")
