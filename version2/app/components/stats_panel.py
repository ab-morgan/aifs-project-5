"""
stats_panel.py

Displays global stats computed during the PREP phase.
"""

from __future__ import annotations

import streamlit as st
import pandas as pd
import altair as alt


def format_percent(val):
    """
    Convert fraction → percentage string safely and visually right-align it
    using figure spaces (\u2007). This avoids Streamlit alignment issues.
    """
    if isinstance(val, (int, float)):
        pct = f"{val * 100:.2f}%"
        return f"\u2007\u2007{pct}"  # visually right-align
    return "N/A"


def render_stats_panel(stats_by_title):
    st.header("📊 Job Market Statistics")

    if not stats_by_title:
        st.info("No statistics available.")
        return

    # Convert dict → DataFrame once
    df = pd.DataFrame(stats_by_title.values())

    # Add formatted percent column
    df["Percent Display"] = df["Percent of Database"].apply(format_percent)

    # ---------------------------------------------------------
    # 📊 OVERALL METRICS
    # ---------------------------------------------------------
    with st.expander("📊 Overall Job Market Metrics", expanded=True):

        median_tenure = df["Median Tenure (Years)"].dropna().median()
        most_common = df.sort_values("Count", ascending=False).iloc[0]

        st.markdown(f"""
        **Total Unique Job Titles:** {len(df):,}  
        **Median Tenure Across All Roles:** {median_tenure:.2f} years  
        **Most Common Job in the Database:** {most_common['Job Title']}  
        **Count:** {most_common['Count']:,}  
        **Percent of Database:** {format_percent(most_common['Percent of Database'])}  
        """)

    # ---------------------------------------------------------
    # 📉 GLOBAL TENURE DISTRIBUTION
    # ---------------------------------------------------------
    with st.expander("📉 Global Tenure Distribution", expanded=False):
        tenure_vals = df["Avg Tenure (Years)"].dropna()

        if len(tenure_vals) > 0:
            chart = (
                alt.Chart(pd.DataFrame({"tenure": tenure_vals}))
                .mark_bar()
                .encode(
                    x=alt.X("tenure:Q", bin=alt.Bin(maxbins=30), title="Tenure (Years)"),
                    y=alt.Y("count()", title="Number of Job Titles"),
                )
            )
            st.altair_chart(chart, width='stretch')
        else:
            st.write("No tenure data available.")

    # ---------------------------------------------------------
    # 🏆 TOP 10 LONGEST TENURE
    # ---------------------------------------------------------
    with st.expander("🏆 Top 10 Longest‑Tenure Roles", expanded=False):
        df2 = df.dropna(subset=["Avg Tenure (Years)"]).copy()
        top10 = df2.sort_values("Avg Tenure (Years)", ascending=False).head(10)

        st.dataframe(
            top10[["Job Title", "Avg Tenure (Years)", "Count", "Frequency Rank"]]
                .reset_index(drop=True),
            width='stretch',
            hide_index=True
        )

    # ---------------------------------------------------------
    # 📈 TOP 10 MOST COMMON ROLES
    # ---------------------------------------------------------
    with st.expander("📈 Top 10 Most Common Roles", expanded=False):
        df3 = df.dropna(subset=["Count"]).copy()
        df3["Computed Rank"] = df3["Count"].rank(method="dense", ascending=False).astype(int)

        top10 = df3.sort_values("Count", ascending=False).head(10)

        # Remove raw decimal column BEFORE renaming
        top10 = top10.drop(columns=["Percent of Database"])
        top10 = top10.rename(columns={"Percent Display": "Percent of Database"})

        st.dataframe(
            top10[["Computed Rank", "Job Title", "Count", "Percent of Database"]]
                .reset_index(drop=True),
            width='stretch',
            hide_index=True
        )

    # ---------------------------------------------------------
    # 🚀 TOP 10 FASTEST-GROWING ROLES
    # ---------------------------------------------------------
    with st.expander("🚀 Top 10 Fastest‑Growing Roles", expanded=False):
        if "Growth Rate" in df.columns:
            df4 = df.dropna(subset=["Growth Rate"]).copy()
            top10 = df4.sort_values("Growth Rate", ascending=False).head(10)

            # Remove raw decimal column BEFORE renaming
            top10 = top10.drop(columns=["Percent of Database"])
            top10 = top10.rename(columns={"Percent Display": "Percent of Database"})

            st.dataframe(
                top10[["Job Title", "Growth Rate", "Count", "Percent of Database"]]
                    .reset_index(drop=True),
                width='stretch',
                hide_index=True
            )
        else:
            st.info("Growth rate data not available.")

    # ---------------------------------------------------------
    # 🏭 INDUSTRY-LEVEL STATS
    # ---------------------------------------------------------
    with st.expander("🏭 Industry‑Level Stats", expanded=False):
        if "Industry" in df.columns:

            industry_summary = (
                df.groupby("Industry")
                .agg({
                    "Count": "sum",
                    "Percent of Database": "sum",
                    "Avg Tenure (Years)": "mean",
                })
                .sort_values("Count", ascending=False)
            )

            # Replace raw decimal with formatted percent
            industry_summary["Percent of Database"] = industry_summary["Percent of Database"].apply(format_percent)

            st.dataframe(
                industry_summary.reset_index()[["Industry", "Count", "Percent of Database", "Avg Tenure (Years)"]],
                width='stretch',
                hide_index=True
            )

            chart = (
                alt.Chart(industry_summary.reset_index())
                .mark_bar()
                .encode(
                    x=alt.X("Industry:N", sort="-y"),
                    y=alt.Y("Count:Q"),
                    tooltip=["Industry", "Count", "Percent of Database"]
                )
            )
            st.altair_chart(chart, width='stretch')

        else:
            st.info("Industry data not available.")


    # ---------------------------------------------------------
    # 📚 BROWSE ALL JOB STATS
    # ---------------------------------------------------------
    with st.expander("Browse All Job Stats"):

        df_all = pd.DataFrame(stats_by_title.values())

        # 1) Format Percent of Database
        df_all["Percent of Database"] = df_all["Percent of Database"].apply(format_percent)

        # 2) Format Top Transitions using your REAL schema
        def format_transitions(val):
            if not isinstance(val, list):
                return ""
            parts = []
            for item in val[:5]:
                if not isinstance(item, dict):
                    continue
                title = item.get("next_job_title", "").strip()
                pct = item.get("percent")
                pct_str = f"{pct * 100:.1f}%" if isinstance(pct, (int, float)) else ""
                if title and pct_str:
                    parts.append(f"{title} ({pct_str})")
            return "; ".join(parts)

        if "Top Transitions" in df_all.columns:
            df_all["Top Transitions"] = df_all["Top Transitions"].apply(format_transitions)

        # ⭐ CRITICAL FIX: convert ALL object columns to strings
        for col in df_all.columns:
            if df_all[col].dtype == "object":
                df_all[col] = df_all[col].astype(str)

        # Reset index to avoid any truncation behavior
        df_all = df_all.reset_index(drop=True)

        st.dataframe(
            df_all,
            width='stretch',
            hide_index=True
        )
