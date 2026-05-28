import streamlit as st
from services.visualization_service import (
    make_sankey,
    make_multilevel_sankey
)


# ---------------------------------------------------------
# 1. Single‑level Sankey
# ---------------------------------------------------------
def render_sankey_panel(prep):
    st.header("Career Transition Flow (Sankey Diagram)")

    mode = st.radio(
        "View transitions by:",
        ["Starting Job → Next Jobs", "Ending Job ← Previous Jobs"],
        horizontal=True
    )

    job = st.selectbox("Select a job title:", sorted(prep["all_titles"]))

    if mode == "Starting Job → Next Jobs":
        transitions = prep["transitions_forward"].get(job, [])
        source_labels = [job] * len(transitions)
        target_labels = [t[0] for t in transitions]
        values = [t[1] for t in transitions]

    else:
        transitions = prep["transitions_reverse"].get(job, [])
        source_labels = [t[0] for t in transitions]
        target_labels = [job] * len(transitions)
        values = [t[1] for t in transitions]

    if not transitions:
        st.info("No transition data available for this job.")
        return

    fig = make_sankey(source_labels, target_labels, values)
    st.plotly_chart(fig, width='stretch')



# ---------------------------------------------------------
# 2. Multi‑Level Sankey (NEW — uses pruning + depth limit)
# ---------------------------------------------------------
def render_multilevel_sankey(prep):
    st.header("Multi‑Level Career Flow")

    # User selects job
    job = st.selectbox("Select a starting job:", sorted(prep["all_titles"]))

    # User selects fan‑out limit (3–5)
    max_fanout = st.slider(
        "Max transitions per node (fan‑out limit):",
        min_value=3,
        max_value=5,
        value=5,
        step=1,
        help="Limits how many transitions each job can expand into. Prevents overload."
    )

    # Build transition map for the engine
    transition_map = {
        src: [{"target": t[0], "count": t[1]} for t in transitions]
        for src, transitions in prep["transitions_forward"].items()
    }

    # Generate pruned, depth‑limited Sankey data
    sankey_data, warnings = make_multilevel_sankey(
        start_job=job,
        transitions_by_source=transition_map,
        max_fanout=max_fanout
    )

    # Display warnings (pruning, collapsing, etc.)
    for w in warnings:
        st.warning(w)

    # Render the diagram
    import plotly.graph_objects as go
    fig = go.Figure(go.Sankey(**sankey_data))
    st.plotly_chart(fig, width='stretch')
