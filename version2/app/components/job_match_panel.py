"""
job_match_panel.py

Displays job match results in a clean, readable format.
"""

from __future__ import annotations

import streamlit as st
import pandas as pd
import altair as alt

def render_job_matches(rows, num_matches):
    st.header("Top Job Matches")

    if not rows:
        st.info("No matches found.")
        return

    for i, row in enumerate(rows[:num_matches], start=1):
        #with st.expander(f"{i}. {row['title']} — Match Score: {row['similarity']:.1f}%"):
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
            # Job Title + Description
            # ---------------------------
            st.markdown(f"### {title}")
            st.markdown(f"**Job Description:** {description}")

            st.markdown("---")

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
            # Match Explanation (optional)
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
            # Skill Gaps (optional)
            # ---------------------------
            skill_gaps = row.get("skill_gaps")
            if skill_gaps:
                with st.expander("🛠 Skill Gap Analysis", expanded=False):
                    st.write("You may be missing:")
                    st.write(", ".join(skill_gaps))
