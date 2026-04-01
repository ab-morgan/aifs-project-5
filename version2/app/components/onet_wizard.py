"""
onet_wizard.py

Modal wizard for the O*NET Mini-IP Interest Profiler (30 questions).

Flow:
  1. Fetch questions from O*NET API on first open
  2. Display questions in pages of 5, with 1-5 Likert radio buttons
  3. On final page submit, POST answers to O*NET results endpoint
  4. Store RIASEC scores in st.session_state["riasec_scores"]
  5. Close dialog — sidebar reads and displays the scores

Usage:
    from app.components.onet_wizard import render_onet_wizard
    render_onet_wizard()   # call from main tab when show_onet is True
"""

from __future__ import annotations
import streamlit as st
from services.onet_service import fetch_questions, fetch_results, OnetServiceError

_PAGE_SIZE = 5

_LABELS = {
    1: "Strongly Dislike",
    2: "Dislike",
    3: "Unsure",
    4: "Like",
    5: "Strongly Like",
}

_AREA_LABELS = {
    "realistic":     "Realistic",
    "investigative": "Investigative",
    "artistic":      "Artistic",
    "social":        "Social",
    "enterprising":  "Enterprising",
    "conventional":  "Conventional",
}


def _load_questions():
    """Fetch questions once and cache in session_state."""
    if "onet_questions" not in st.session_state:
        with st.spinner("Loading questionnaire…"):
            try:
                st.session_state["onet_questions"] = fetch_questions()
                st.session_state["onet_error"] = None
            except OnetServiceError as e:
                st.session_state["onet_questions"] = []
                st.session_state["onet_error"] = str(e)


def _current_page() -> int:
    return st.session_state.get("onet_page", 0)


def _answers() -> dict[int, int]:
    return st.session_state.setdefault("onet_answers", {})


@st.dialog("O*NET Interest Profiler", width="large")
def render_onet_wizard():
    _load_questions()

    questions = st.session_state.get("onet_questions", [])
    error = st.session_state.get("onet_error")

    if error:
        st.error(f"Could not load questionnaire: {error}")
        if st.button("Close"):
            st.session_state["show_onet"] = False
            st.rerun()
        return

    if not questions:
        st.warning("No questions available.")
        return

    total_q = len(questions)
    total_pages = (total_q + _PAGE_SIZE - 1) // _PAGE_SIZE
    page = _current_page()
    answers = _answers()

    # ── Progress bar ─────────────────────────────────────
    answered = len(answers)
    st.progress(answered / total_q, text=f"{answered} of {total_q} answered")
    st.markdown("---")

    # ── Current page questions ────────────────────────────
    start_idx = page * _PAGE_SIZE
    end_idx = min(start_idx + _PAGE_SIZE, total_q)
    page_questions = questions[start_idx:end_idx]

    st.markdown(
        f"**Questions {start_idx + 1}–{end_idx}** of {total_q} &nbsp;·&nbsp; "
        f"Page {page + 1} of {total_pages}",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='font-size:0.82rem;color:#888;margin-bottom:12px;'>"
        "How would you feel about doing each of these activities?"
        "</div>",
        unsafe_allow_html=True,
    )

    for q in page_questions:
        idx = q["index"]
        area = _AREA_LABELS.get(q["area"], q["area"].title())
        text = q["text"]
        current_val = answers.get(idx)

        # Map stored int → label for default
        options = list(_LABELS.values())
        default_idx = (current_val - 1) if current_val else None

        st.markdown(
            f'<div style="font-size:0.78rem;color:#14b8a6;margin-bottom:2px;">{area}</div>'
            f'<div style="font-weight:600;margin-bottom:6px;">{idx}. {text}</div>',
            unsafe_allow_html=True,
        )
        choice = st.radio(
            label=f"q_{idx}",
            options=options,
            index=default_idx,
            horizontal=True,
            key=f"onet_q_{idx}",
            label_visibility="collapsed",
        )
        if choice:
            # Reverse map label → value
            answers[idx] = next(v for v, l in _LABELS.items() if l == choice)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    st.markdown("---")

    # ── Navigation ────────────────────────────────────────
    col_back, col_spacer, col_next = st.columns([1, 4, 1])

    with col_back:
        if page > 0:
            if st.button("← Back", use_container_width=True):
                st.session_state["onet_page"] = page - 1
                st.rerun()

    with col_next:
        page_answered = all(answers.get(q["index"]) for q in page_questions)
        is_last = page == total_pages - 1

        if is_last:
            all_answered = len(answers) == total_q
            if st.button(
                "Submit",
                type="primary",
                use_container_width=True,
                disabled=not all_answered,
            ):
                _submit_answers(answers, total_q)
        else:
            if st.button(
                "Next →",
                type="primary",
                use_container_width=True,
                disabled=not page_answered,
            ):
                st.session_state["onet_page"] = page + 1
                st.rerun()

    # ── Cancel ────────────────────────────────────────────
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    if st.button("Cancel", use_container_width=True):
        _reset_wizard()
        st.rerun()


def _submit_answers(answers: dict[int, int], total_q: int):
    """Build answer string, call O*NET results API, store RIASEC scores."""
    answer_str = "".join(str(answers.get(i, 3)) for i in range(1, total_q + 1))
    with st.spinner("Calculating your interest profile…"):
        try:
            results = fetch_results(answer_str)
        except OnetServiceError as e:
            st.error(f"Could not retrieve results: {e}")
            return

    # Store as {Title: score} for sidebar display
    riasec = {r["title"]: r["score"] for r in results}
    st.session_state["riasec_scores"] = riasec
    st.session_state["riasec_full"] = results  # keep full data with descriptions
    _reset_wizard()
    st.success("Interest profile saved!")
    st.rerun()


def _reset_wizard():
    for key in ["onet_page", "onet_answers", "onet_questions", "onet_error", "show_onet"]:
        st.session_state.pop(key, None)
