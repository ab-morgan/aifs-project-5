"""
visualization_service.py

Centralized module for all visualizations used in the application:
Sankey diagrams, histograms, bar charts, and future analytics visuals.
"""

from __future__ import annotations
from typing import List
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

def make_global_tenure_histogram(values):
    return make_histogram(
        values,
        title="Global Tenure Distribution",
        x_label="Tenure (Years)",
        y_label="Number of Job Titles"
    )

def prune_transitions(transitions, max_fanout):
    """
    transitions: list of dicts like:
        [{"target": "Job B", "count": 42}, ...]
    max_fanout: int (3–5)

    Returns:
        pruned list + optional "Other" bucket
    """
    # Sort by frequency descending
    sorted_transitions = sorted(transitions, key=lambda x: x["count"], reverse=True)

    if len(sorted_transitions) <= max_fanout:
        return sorted_transitions, None

    kept = sorted_transitions[:max_fanout]
    other = sorted_transitions[max_fanout:]

    other_count = sum(t["count"] for t in other)
    other_node = {"target": "Other", "count": other_count}

    return kept + [other_node], other_node

def expand_multilevel(start_job, transitions_by_source, max_depth, max_fanout):
    """
    transitions_by_source: dict mapping job -> list of transitions
    max_depth: fixed at 2
    max_fanout: 3–5

    Returns:
        nodes, links, warnings
    """
    nodes = set()
    links = []
    warnings = []

    frontier = [(start_job, 0)]
    nodes.add(start_job)

    while frontier:
        job, depth = frontier.pop(0)

        if depth >= max_depth:
            continue

        outgoing = transitions_by_source.get(job, [])
        pruned, other_node = prune_transitions(outgoing, max_fanout)

        # Warning if pruning occurred
        if other_node:
            warnings.append(
                f"{job} has many transitions; showing top {max_fanout} and collapsing the rest into 'Other'."
            )

        for t in pruned:
            target = t["target"]
            count = t["count"]

            nodes.add(target)
            links.append({"source": job, "target": target, "value": count})

            # Only expand real nodes, not "Other"
            if target != "Other":
                frontier.append((target, depth + 1))

    return list(nodes), links, warnings


# ---------------------------------------------------------
# SANKEY DIAGRAM
# ---------------------------------------------------------

def make_sankey(source_labels: List[str], target_labels: List[str], values: List[int]):
    """
    Creates a Sankey diagram using Plotly.
    source_labels: list of source job titles
    target_labels: list of target job titles
    values: list of counts
    """

    # Count unique nodes
    unique_nodes = set(source_labels) | set(target_labels)
    node_count = len(unique_nodes)

    # Dynamic height: 40px per node, minimum 500px, max 2000px
    height = min(max(40 * node_count, 500), 2000)

    # Build node list
    labels = list(unique_nodes)
    label_to_index = {label: i for i, label in enumerate(labels)}

    source_idx = [label_to_index[s] for s in source_labels]
    target_idx = [label_to_index[t] for t in target_labels]

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            label=labels,
        ),
        link=dict(
            source=source_idx,
            target=target_idx,
            value=values,
        )
    )])

    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=20, b=20)
    )

    return fig


# ---------------------------------------------------------
# HISTOGRAM
# ---------------------------------------------------------
def make_histogram(values, title: str, x_label: str = "", y_label: str = "Count"):
    """
    Creates a histogram using Plotly Express.
    """
    fig = px.histogram(
        x=values,
        nbins=30,
        title=title,
        labels={"x": x_label, "y": y_label}
    )
    fig.update_layout(bargap=0.1)
    return fig


# ---------------------------------------------------------
# BAR CHART
# ---------------------------------------------------------
def make_bar_chart(labels: List[str], values: List[float], title: str):
    """
    Creates a bar chart using Plotly Express.
    """
    fig = px.bar(
        x=labels,
        y=values,
        title=title,
        labels={"x": "Category", "y": "Value"}
    )
    fig.update_layout(xaxis_tickangle=-45)
    return fig


# ---------------------------------------------------------
# MULTILEVEL SANKEY CHART
# ---------------------------------------------------------

def render_multilevel_sankey(prep):
    st.header("Multi‑Level Career Flow")

    job = st.selectbox("Select a starting job:", sorted(prep["all_titles"]))

    level1 = prep["transitions_forward"].get(job, [])
    if not level1:
        st.info("No transitions available for this job.")
        return

    # Build second-level transitions
    source_labels = []
    target_labels = []
    values = []

    for (next_job, count1) in level1:
        # First hop
        source_labels.append(job)
        target_labels.append(next_job)
        values.append(count1)

        # Second hop
        level2 = prep["transitions_forward"].get(next_job, [])
        for (next2, count2) in level2:
            source_labels.append(next_job)
            target_labels.append(next2)
            values.append(count2)

    fig = make_sankey(source_labels, target_labels, values)
    st.plotly_chart(fig, width='stretch')

def make_multilevel_sankey(start_job, transitions_by_source, max_fanout=5):
    """
    max_fanout: user‑selectable (3–5)
    """
    MAX_DEPTH = 2

    nodes, links, warnings = expand_multilevel(
        start_job=start_job,
        transitions_by_source=transitions_by_source,
        max_depth=MAX_DEPTH,
        max_fanout=max_fanout,
    )

    # Convert nodes to index mapping for Plotly
    node_index = {name: i for i, name in enumerate(nodes)}

    sankey_data = {
        "node": {"label": nodes},
        "link": {
            "source": [node_index[l["source"]] for l in links],
            "target": [node_index[l["target"]] for l in links],
            "value": [l["value"] for l in links],
        },
    }

    return sankey_data, warnings
