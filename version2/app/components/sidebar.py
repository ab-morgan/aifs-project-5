"""
sidebar.py

Redesigned sidebar matching the Career Match AI layout:
- Resume upload
- Interest Profile (RIASEC scores + questionnaire link)
- Preferences free-text
- Exclusions free-text
- Results count selector + Find Matches button
"""

from __future__ import annotations
import html
import streamlit as st


_CONTROL_CHARS = str.maketrans("", "", "".join(chr(i) for i in range(32) if i not in (9, 10, 13)))


def _sanitize_text(text: str) -> str:
    """Strip null bytes and non-printable control characters from resume text."""
    return text.translate(_CONTROL_CHARS).strip()


def _read_uploaded_file(uploaded_file) -> str:
    if uploaded_file is None:
        return ""
    if uploaded_file.name.endswith(".pdf"):
        import PyPDF2
        reader = PyPDF2.PdfReader(uploaded_file)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if uploaded_file.name.endswith(".docx"):
        import docx
        doc = docx.Document(uploaded_file)
        return "\n".join(p.text for p in doc.paragraphs)
    if uploaded_file.name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8", errors="ignore")
    return ""


def render_sidebar(session_id: str):
    sb = st.sidebar
    config = st.session_state.get("config")
    limits = config.limits if config else None
    max_chars = limits.max_resume_chars if limits else 50000
    max_mb = limits.max_upload_mb if limits else 5

    # ── Resume ──────────────────────────────────────────
    sb.markdown('<div class="sidebar-section-label">Resume</div>', unsafe_allow_html=True)
    uploaded = sb.file_uploader(
        f"Upload a file (PDF, DOCX, TXT — max {max_mb} MB)",
        type=["pdf", "docx", "txt"],
        label_visibility="visible",
    )
    sb.caption(f"Or paste your resume text below (max {max_chars:,} characters)")
    pasted = sb.text_area(
        "",
        key="resume_text_input",
        placeholder="Paste resume text here…",
        height=160,
        label_visibility="collapsed",
        max_chars=max_chars,
    )

    # ── Interest Profile ─────────────────────────────────
    sb.markdown('<div class="sidebar-section-label">Interest Profile</div>', unsafe_allow_html=True)
    sb.caption("Optional: Complete questionnaire for better matches")

    riasec = st.session_state.get("riasec_scores")
    if riasec:
        for label, score in riasec.items():
            sb.markdown(
                f'<div class="riasec-row"><span>{label}</span>'
                f'<span class="riasec-score">{score}</span></div>',
                unsafe_allow_html=True,
            )
        sb.markdown('<div style="margin-top:4px;font-size:0.75rem;color:#14b8a6;">✓ Profile completed</div>',
                    unsafe_allow_html=True)
    else:
        sb.markdown(
            '<div style="font-size:0.8rem;color:#888;margin-bottom:6px;">'
            'No profile yet.</div>',
            unsafe_allow_html=True,
        )

    if sb.button("Take O*NET Interest Questionnaire", use_container_width=True):
        st.session_state["show_onet"] = True

    # ── Preferences ──────────────────────────────────────
    sb.markdown('<div class="sidebar-section-label">Preferences</div>', unsafe_allow_html=True)
    sb.caption("What you're looking for")
    preferences = sb.text_area(
        "",
        key="preferences_input",
        placeholder="e.g. Remote work, product-focused companies, good work-life balance…",
        height=90,
        label_visibility="collapsed",
    )

    # ── Exclusions ───────────────────────────────────────
    sb.markdown('<div class="sidebar-section-label">Exclusions</div>', unsafe_allow_html=True)
    sb.caption("What to avoid")
    exclusions = sb.text_area(
        "",
        key="exclusions_input",
        placeholder="e.g. Startups under 10 people, on-call heavy roles…",
        height=90,
        label_visibility="collapsed",
    )

    # ── Results ──────────────────────────────────────────
    sb.markdown('<div class="sidebar-section-label">Results</div>', unsafe_allow_html=True)
    sb.caption("Number of matches")

    count_options = [5, 10, 15, 20]
    current = st.session_state.get("num_matches", 10)
    cols = sb.columns(len(count_options))
    for col, n in zip(cols, count_options):
        btn_type = "primary" if n == current else "secondary"
        if col.button(str(n), key=f"count_btn_{n}", type=btn_type, use_container_width=True):
            st.session_state["num_matches"] = n
            st.rerun()

    sb.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    submitted = sb.button("Find Matches", type="primary", use_container_width=True)

    # ── Return resume text on submit ─────────────────────
    if submitted:
        # File upload takes priority over pasted text
        if uploaded:
            # Enforce file size limit
            file_size_mb = uploaded.size / (1024 * 1024)
            if file_size_mb > max_mb:
                sb.error(f"File is {file_size_mb:.1f} MB. Maximum allowed is {max_mb} MB.")
                return None
            text = _read_uploaded_file(uploaded)
            if len(text) > max_chars:
                sb.error(f"Resume content exceeds {max_chars:,} characters after extraction. Please shorten it.")
                return None
            if text.strip():
                st.session_state["preferences"] = preferences
                st.session_state["exclusions"] = exclusions
                return _sanitize_text(text)
        if pasted.strip():
            # max_chars is already enforced by the text_area widget, but double-check
            if len(pasted) > max_chars:
                sb.error(f"Pasted text exceeds {max_chars:,} characters.")
                return None
            st.session_state["preferences"] = preferences
            st.session_state["exclusions"] = exclusions
            return _sanitize_text(pasted)
        sb.warning("Please upload a file or paste your resume text before finding matches.")

    return None
