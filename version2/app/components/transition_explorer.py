import streamlit as st
import pandas as pd

def render_transition_explorer(prep):
    st.header("Transition Explorer")

    # ---------------------------
    # Filters
    # ---------------------------
    min_count = st.slider("Minimum transition count:", 1, 50, 5)

    # Industry dropdown (now using prep["industries"])
    industry_filter = st.selectbox(
        "Filter by industry:",
        ["Any"] + prep["industries"]
    )

    growth_filter = st.selectbox(
        "Filter by growth rate:",
        ["Any", "Positive", "Negative", "Zero"]
    )

    # ---------------------------
    # Build filtered transition table
    # ---------------------------
    rows = []

    for job, transitions in prep["transitions_forward"].items():
        job_industry = prep["stats"][job].get("industry")

        for (next_job, count) in transitions:
            if count < min_count:
                continue

            next_industry = prep["stats"][next_job].get("industry")

            # Industry filter
            if industry_filter != "Any":
                if industry_filter not in (job_industry, next_industry):
                    continue

            # Growth filter
            gr = prep["stats"][next_job].get("growth_rate")
            if growth_filter != "Any" and gr is not None:
                if growth_filter == "Positive" and gr <= 0:
                    continue
                if growth_filter == "Negative" and gr >= 0:
                    continue
                if growth_filter == "Zero" and gr != 0:
                    continue

            rows.append({
                "From Job": job,
                "To Job": next_job,
                "Count": count,
                "From Industry": job_industry,
                "To Industry": next_industry,
                "Growth Rate": gr,
            })

    # ---------------------------
    # Display results
    # ---------------------------
    if not rows:
        st.info("No transitions match your filters.")
        return

    df = pd.DataFrame(rows)
    st.dataframe(df, width='stretch')
