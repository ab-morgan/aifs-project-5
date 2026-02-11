"""
sidebar.py

Handles:
- Resume upload
- Resume text input
- Model selection display (read-only)
- Session ID display
"""

from __future__ import annotations

import streamlit as st


def _read_uploaded_file(uploaded_file) -> str:
    """Extract text from uploaded PDF or DOCX."""
    if uploaded_file is None:
        return ""

    if uploaded_file.name.endswith(".pdf"):
        import PyPDF2
        reader = PyPDF2.PdfReader(uploaded_file)
        return "\n".join(page.extract_text() for page in reader.pages)

    if uploaded_file.name.endswith(".docx"):
        import docx
        doc = docx.Document(uploaded_file)
        return "\n".join(p.text for p in doc.paragraphs)

    return ""


def render_sidebar(session_id):
    st.sidebar.header("Resume Input")

    st.sidebar.markdown(
        "<div class='sidebar-instructions'>"
        "Upload a resume file or paste your resume text below."
        "</div>",
        unsafe_allow_html=True
    )


    uploaded = st.sidebar.file_uploader("Upload Resume", type=["pdf", "docx", "txt"])
    text_input = st.sidebar.text_area("Paste Resume Text", height=200)

    # ⭐ Add a real submit button
    st.sidebar.markdown("<div class='sidebar-spacer'></div>", unsafe_allow_html=True)
    submitted = st.sidebar.button("Submit Resume", type="primary")

    num_matches = st.sidebar.slider(
        "Number of matches to display",
        min_value=1,
        max_value=20,
        value=10,
        step=1
    )

    st.session_state["num_matches"] = num_matches


    # Return only when the user actually clicks submit
    if submitted:
        if uploaded:
            return uploaded
        if text_input.strip():
            return text_input

        st.sidebar.warning("Please upload a file or paste text before submitting.")
        return None

    return None
