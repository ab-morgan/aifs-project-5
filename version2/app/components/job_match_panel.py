"""
job_match_panel.py

Displays job match results in a clean, readable format.
"""

from __future__ import annotations

import streamlit as st
from services.match_explanation_service import explain_match, MatchExplanationError, MatchExplanationRateLimitError


def _build_print_html(selected_rows: list[dict]) -> str:
    """Build a print-ready HTML document for the selected job matches."""
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
        avg_tenure_display = f"{avg_tenure:.2f} years" if avg_tenure is not None else "N/A"
        median_tenure_display = f"{median_tenure:.2f} years" if median_tenure is not None else "N/A"

        explanation_html = (
            f"<p>{explanation}</p>"
            if explanation and not explanation.startswith("__")
            else "<p><em>Not available</em></p>"
        )

        items_html += f"""
        <div class="job">
            <h2>{idx}. {title}</h2>
            <p class="score">Match Score: <strong>{similarity:.1f}%</strong></p>
            <h3>Description</h3>
            <p>{description}</p>
            <h3>Why This Job Matches Your Experience</h3>
            {explanation_html}
            <h3>Job Insights</h3>
            <table>
                <tr><td>Percent of Database</td><td>{pct_display}</td></tr>
                <tr><td>Frequency Rank</td><td>{freq_display}</td></tr>
                <tr><td>Average Tenure</td><td>{avg_tenure_display}</td></tr>
                <tr><td>Median Tenure</td><td>{median_tenure_display}</td></tr>
            </table>
        </div>
        """

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>CareerPivots — Job Matches</title>
<style>
  body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; color: #222; }}
  h1 {{ border-bottom: 2px solid #333; padding-bottom: 8px; }}
  .job {{ border: 1px solid #ddd; border-radius: 6px; padding: 20px; margin-bottom: 30px; }}
  .score {{ color: #2a7ae2; font-size: 1.1em; }}
  h2 {{ margin-top: 0; }}
  h3 {{ margin-top: 16px; color: #444; }}
  table {{ border-collapse: collapse; width: 100%; }}
  td {{ padding: 6px 10px; border: 1px solid #ddd; }}
  td:first-child {{ font-weight: bold; width: 200px; }}
  @media print {{ .job {{ page-break-inside: avoid; }} }}
</style>
</head>
<body>
<h1>CareerPivots — Job Match Report</h1>
{items_html}
</body>
</html>"""


def render_job_matches(num_matches=10):
    st.header("Top Job Matches")

    # -----------------------------
    # Clear Results button
    # -----------------------------
    if st.button("Clear Results"):
        st.session_state.pop("job_match_results", None)
        st.session_state.pop("selected_match_indices", None)
        st.session_state["has_run_matching"] = False
        st.rerun()

    if not st.session_state.get("has_run_matching", False):
        return

    rows = st.session_state.get("job_match_results")
    if not rows:
        st.info("No matches found. Upload a resume and generate matches to see results here.")
        return

    # Persist selected indices across tab switches
    if "selected_match_indices" not in st.session_state:
        st.session_state["selected_match_indices"] = set()

    # Recompute selected set from checkbox widget values so the count
    # is always current on the same render pass (avoids off-by-one).
    selected_indices = {
        idx for idx in range(len(rows[:num_matches]))
        if st.session_state.get(f"select_match_{idx + 1}", False)
    }
    st.session_state["selected_match_indices"] = selected_indices

    # -----------------------------
    # Print / Export section
    # -----------------------------
    if selected_indices:
        st.markdown(f"**{len(selected_indices)} match(es) selected for export.**")
        selected_rows = []
        for idx in sorted(selected_indices):
            row = rows[idx]
            selected_rows.append({
                "row": row,
                "explanation": st.session_state.get(f"explanation_{idx + 1}"),
            })
        html_doc = _build_print_html(selected_rows)
        st.download_button(
            label="Download Selected Matches (HTML)",
            data=html_doc,
            file_name="job_matches.html",
            mime="text/html",
        )
    else:
        st.caption("Check the box on any match below to add it to your export list.")

    st.divider()

    # -----------------------------
    # Render each job match
    # -----------------------------
    for i, row in enumerate(rows[:num_matches], start=1):
        idx = i - 1  # 0-based index for session_state set

        title = row["title"]
        similarity = row["similarity"]
        description = row.get("description", "No description available.")

        stats = row.get("stats", {})
        pct = stats.get("percent_of_db")
        freq = stats.get("frequency_rank")
        avg_tenure = stats.get("avg_tenure_years")
        median_tenure = stats.get("median_tenure_years")

        pct_display = f"{pct * 100:.2f}%" if pct is not None else "N/A"
        freq_display = freq if freq is not None else "N/A"
        avg_tenure_display = f"{avg_tenure:.2f} years" if avg_tenure is not None else "N/A"
        median_tenure_display = f"{median_tenure:.2f} years" if median_tenure is not None else "N/A"

        with st.expander(f"{i}. {title} — Match Score: {similarity:.1f}%"):

            # ---------------------------
            # Select for export
            # ---------------------------
            is_selected = idx in selected_indices
            st.checkbox("Include in export", value=is_selected, key=f"select_match_{i}")

            # ---------------------------
            # Job Title + Description
            # ---------------------------
            st.markdown(f"### {title}")
            st.markdown(f"**Job Description:** {description}")

            # ---------------------------
            # LLM Match Explanation
            # ---------------------------
            if "experiences" in st.session_state:
                with st.expander("Why this job matches your experience"):
                    cache_key = f"explanation_{i}"
                    retry_key = f"retry_explanation_{i}"

                    if st.session_state.get(retry_key):
                        st.session_state.pop(cache_key, None)
                        st.session_state[retry_key] = False

                    if cache_key not in st.session_state:
                        try:
                            st.session_state[cache_key] = explain_match(
                                st.session_state["experiences"],
                                row,
                                st.session_state["config"].resume_extraction
                            )
                        except MatchExplanationRateLimitError:
                            st.session_state[cache_key] = "__rate_limited__"
                        except MatchExplanationError as e:
                            st.session_state[cache_key] = f"__error__{e}"

                    result = st.session_state.get(cache_key)
                    if result == "__rate_limited__":
                        st.warning("Request limit reached. Please wait a moment, then try again.")
                        if st.button("Retry", key=f"btn_retry_{i}"):
                            st.session_state[retry_key] = True
                            st.rerun()
                    elif isinstance(result, str) and result.startswith("__error__"):
                        st.write(f"Could not generate explanation: {result[9:]}")
                    else:
                        st.write(result)

            # ---------------------------
            # Job Statistics
            # ---------------------------
            st.markdown("### 📊 Job Insights")
            st.markdown(f"""
            - **Percent of Database:** {pct_display}  
            - **Frequency Rank:** {freq_display}  
            - **Average Tenure:** {avg_tenure_display}  
            - **Median Tenure:** {median_tenure_display}  
            """)

            top_transitions = stats.get("top_transitions") or []
            if top_transitions:
                st.markdown("**Top Transitions:**")
                for t in top_transitions[:3]:
                    st.markdown(f"- {t['next_job_title']} — {t['percent'] * 100:.1f}%")
            else:
                st.markdown("**Top Transitions:** N/A")

            # ---------------------------
            # Keyword-based Explanation
            # ---------------------------
            explanation = row.get("explanation")
            if explanation:
                with st.expander("🧠 Why This Job Matches", expanded=False):
                    st.write(f"**Similarity Score:** {explanation['similarity']:.3f}")
                    st.write(f"**Keyword Overlap:** {explanation['overlap_count']} words")
                    st.write(f"**Missing Keywords:** {explanation['missing_count']} words")
                    st.write("**Top Overlapping Keywords:**")
                    st.write(", ".join(explanation["top_overlap"]))
                    st.write("**Top Missing Keywords:**")
                    st.write(", ".join(explanation["top_missing"]))

            # ---------------------------
            # Skill Gaps
            # ---------------------------
            skill_gaps = row.get("skill_gaps")
            if skill_gaps:
                with st.expander("🛠 Skill Gap Analysis", expanded=False):
                    st.write("You may be missing:")
                    st.write(", ".join(skill_gaps))
