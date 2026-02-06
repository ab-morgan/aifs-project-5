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


def render_sidebar(session_id: str) -> str:
    st.sidebar.title("Resume Input")

    st.sidebar.markdown(f"**Session ID:** `{session_id}`")

    uploaded = st.sidebar.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"])
    resume_text = st.sidebar.text_area("Or paste your resume text here")

    extracted_text = ""
    if uploaded:
        extracted_text = _read_uploaded_file(uploaded)

    final_text = extracted_text or resume_text

    if final_text:
        st.sidebar.success("Resume loaded.")
        return final_text

    st.sidebar.info("Upload a resume or paste text to begin.")
    return ""
