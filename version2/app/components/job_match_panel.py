"""
job_match_panel.py

Redesigned job match panel matching the Career Match AI screenshot:
- Flat cards (no expanders) with score badge
- Inline "Why this matches" section
- Job Insights row
- Top Career Transitions with bar chart
- Select for export checkbox + Select All
"""

from __future__ import annotations
import streamlit as st
from services.match_explanation_service import (
    explain_match, MatchExplanationError, MatchExplanationRateLimitError
)


def _bar(pct: float, max_pct: float = 0.5) -> str:
    """Render an inline HTML progress bar for transitions."""
    fill = min(int((pct / max_pct) * 100), 100)
    return (
        f'<div class="transition-bar-bg">'
        f'<div class="transition-bar-fill" style="width:{fill}%"></div>'
        f'</div>'
    )


def _render_explanation(i: int, row: dict):
    cache_key = f"explanation_{i}"
    retry_key = f"retry_explanation_{i}"

    if st.session_state.get(retry_key):
        st.session_state.pop(cache_key, None)
        st.session_state[retry_key] = False

    if cache_key not in st.session_state:
        with st.spinner(""):
            try:
                st.session_state[cache_key] = explain_match(
                    st.session_state["experiences"],
                    row,
                    st.session_state["config"].resume_extraction,
                )
            except MatchExplanationRateLimitError:
                st.session_state[cache_key] = "__rate_limited__"
            except MatchExplanationError as e:
                st.session_state[cache_key] = f"__error__{e}"

    result = st.session_state.get(cache_key, "")

    if result == "__rate_limited__":
        st.warning("Request limit reached. Please wait a moment, then try again.")
        if st.button("Retry", key=f"btn_retry_{i}"):
            st.session_state[retry_key] = True
            st.rerun()
        return ""
    if isinstance(result, str) and result.startswith("__error__"):
        return ""
    return result or ""


def _render_card(i: int, row: dict, is_selected: bool):
    title = row["title"]
    similarity = row["similarity"]
    description = row.get("description", "No description available.")

    stats = row.get("stats", {})
    pct = stats.get("percent_of_db")
    freq = stats.get("frequency_rank")
    avg_tenure = stats.get("avg_tenure_years")
    median_tenure = stats.get("median_tenure_years")
    top_transitions = stats.get("top_transitions") or []

    pct_display = f"{pct * 100:.2f}%" if pct is not None else "N/A"
    freq_display = f"#{freq}" if freq is not None else "N/A"
    avg_display = f"{avg_tenure:.1f} yrs" if avg_tenure is not None else "N/A"
    med_display = f"{median_tenure:.1f} yrs" if median_tenure is not None else "N/A"

    # ── Card open ────────────────────────────────────────
    st.markdown('<div class="job-card">', unsafe_allow_html=True)

    # Score badge + title row
    st.markdown(
        f'<div class="score-badge">{similarity:.0f}%</div>'
        f'<h3>{title}</h3>'
        f'<div class="job-desc">{description}</div>',
        unsafe_allow_html=True,
    )

    # Select for export checkbox (inline with card)
    col_check, col_spacer = st.columns([1, 8])
    with col_check:
        st.checkbox("Export", value=is_selected, key=f"select_match_{i}", label_visibility="collapsed")

    # ── Why this matches ─────────────────────────────────
    if "experiences" in st.session_state:
        explanation = _render_explanation(i, row)
        if explanation:
            st.markdown(
                f'<div class="why-box">'
                f'<div class="why-label">💡 Why this matches your experience</div>'
                f'<p>{explanation}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── Job Insights ─────────────────────────────────────
    st.markdown(
        f'<div class="insights-row">'
        f'  <div class="insight-cell">'
        f'    <div class="insight-label">Database %</div>'
        f'    <div class="insight-value">{pct_display}</div>'
        f'  </div>'
        f'  <div class="insight-cell">'
        f'    <div class="insight-label">Frequency Rank</div>'
        f'    <div class="insight-value">{freq_display}</div>'
        f'  </div>'
        f'  <div class="insight-cell">'
        f'    <div class="insight-label">Avg Tenure</div>'
        f'    <div class="insight-value">⏱ {avg_display}</div>'
        f'  </div>'
        f'  <div class="insight-cell">'
        f'    <div class="insight-label">Median Tenure</div>'
        f'    <div class="insight-value">⏱ {med_display}</div>'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Top Career Transitions ────────────────────────────
    if top_transitions:
        max_pct = max((t.get("percent", 0) for t in top_transitions[:3]), default=0.01)
        rows_html = ""
        for idx, t in enumerate(top_transitions[:3], start=1):
            t_title = t.get("next_job_title", "")
            t_pct = t.get("percent", 0)
            rows_html += (
                f'<div class="transition-row">'
                f'  <span style="width:16px;color:#aaa;font-size:0.75rem">{idx}.</span>'
                f'  <span class="transition-title">{t_title}</span>'
                f'  {_bar(t_pct, max_pct)}'
                f'  <span class="transition-pct">{t_pct * 100:.1f}%</span>'
                f'</div>'
            )
        st.markdown(
            f'<div class="transitions-section">'
            f'  <div class="transitions-label">↗ Top Career Transitions</div>'
            f'  {rows_html}'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)  # close .job-card


def _build_print_html(selected_rows: list[dict]) -> str:
    items_html = ""
    for idx, entry in enumerate(selected_rows, start=1):
        row = entry["row"]
        title = row["title"]
        similarity = row["similarity"]
        description = row.get("description", "No description available.")
        explanation = entry.get("explanation", "")

        stats = row.get("stats", {})
        pct = stats.get("percent_of_db")
        freq = stats.get("frequency_rank")
        avg_tenure = stats.get("avg_tenure_years")
        median_tenure = stats.get("median_tenure_years")

        pct_display = f"{pct * 100:.2f}%" if pct is not None else "N/A"
        freq_display = str(freq) if freq is not None else "N/A"
        avg_display = f"{avg_tenure:.2f} years" if avg_tenure is not None else "N/A"
        med_display = f"{median_tenure:.2f} years" if median_tenure is not None else "N/A"
        explanation_html = (
            f"<p>{explanation}</p>"
            if explanation and not explanation.startswith("__")
            else "<p><em>Not available</em></p>"
        )

        items_html += f"""
        <div class="job">
            <h2>{idx}. {title} <span class="score">{similarity:.0f}%</span></h2>
            <h3>Description</h3><p>{description}</p>
            <h3>Why This Job Matches Your Experience</h3>{explanation_html}
            <h3>Job Insights</h3>
            <table>
                <tr><td>Percent of Database</td><td>{pct_display}</td></tr>
                <tr><td>Frequency Rank</td><td>{freq_display}</td></tr>
                <tr><td>Average Tenure</td><td>{avg_display}</td></tr>
                <tr><td>Median Tenure</td><td>{med_display}</td></tr>
            </table>
        </div>"""

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Career Match AI — Job Matches</title>
<style>
  body{{font-family:Arial,sans-serif;max-width:800px;margin:40px auto;color:#222}}
  h1{{border-bottom:2px solid #333;padding-bottom:8px}}
  .job{{border:1px solid #ddd;border-radius:6px;padding:20px;margin-bottom:30px}}
  .score{{color:#14b8a6;font-size:0.9em;font-weight:700}}
  h2{{margin-top:0}} h3{{margin-top:16px;color:#444}}
  table{{border-collapse:collapse;width:100%}}
  td{{padding:6px 10px;border:1px solid #ddd}}
  td:first-child{{font-weight:bold;width:200px}}
  @media print{{.job{{page-break-inside:avoid}}}}
</style></head><body>
<h1>Career Match AI — Job Match Report</h1>
{items_html}
</body></html>"""


def render_job_matches(num_matches: int = 10):
    if not st.session_state.get("has_run_matching", False):
        st.markdown(
            '<div style="color:#aaa;text-align:center;padding:60px 0;font-size:0.95rem;">'
            'Upload your resume and click <strong>Find Matches</strong> to get started.'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    rows = st.session_state.get("job_match_results") or []
    if not rows:
        st.info("No matches found.")
        return

    visible = rows[:num_matches]

    # ── Recompute selected set from widget state (avoids off-by-one) ──
    selected_indices = {
        idx for idx in range(len(visible))
        if st.session_state.get(f"select_match_{idx + 1}", False)
    }
    st.session_state["selected_match_indices"] = selected_indices

    # ── Section heading row ───────────────────────────────
    head_col, sel_col = st.columns([6, 1])
    with head_col:
        st.markdown(
            f'<div class="section-heading"><h2>Matched Job Types</h2></div>'
            f'<div class="section-subtext">{len(visible)} job types found</div>',
            unsafe_allow_html=True,
        )
    with sel_col:
        if st.button("Select all", key="select_all_btn"):
            for j in range(1, len(visible) + 1):
                st.session_state[f"select_match_{j}"] = True
            st.rerun()

    # ── Export bar ────────────────────────────────────────
    if selected_indices:
        exp_col, dl_col = st.columns([5, 2])
        with exp_col:
            st.markdown(
                f'<div style="font-size:0.85rem;color:#555;padding-top:6px;">'
                f'{len(selected_indices)} match(es) selected for export</div>',
                unsafe_allow_html=True,
            )
        with dl_col:
            selected_rows = [
                {"row": rows[idx], "explanation": st.session_state.get(f"explanation_{idx + 1}")}
                for idx in sorted(selected_indices)
            ]
            st.download_button(
                "Download (HTML)",
                data=_build_print_html(selected_rows),
                file_name="job_matches.html",
                mime="text/html",
                use_container_width=True,
            )

    # ── Cards ─────────────────────────────────────────────
    for i, row in enumerate(visible, start=1):
        is_selected = (i - 1) in selected_indices
        _render_card(i, row, is_selected)

    # ── Clear button ──────────────────────────────────────
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("Clear Results", key="clear_results_btn"):
        for key in list(st.session_state.keys()):
            if key.startswith(("explanation_", "select_match_", "retry_explanation_")):
                del st.session_state[key]
        st.session_state.pop("job_match_results", None)
        st.session_state.pop("selected_match_indices", None)
        st.session_state["has_run_matching"] = False
        st.rerun()
