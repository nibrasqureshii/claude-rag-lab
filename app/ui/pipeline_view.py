"""Renders the step-by-step flow a question moves through, plus expandable
detail per step -- what was retrieved, what was sent to Claude, and what
came back. This is what makes "retrieval and generation are separate
steps" something you can see happen, not just a claim in prose.
"""

from __future__ import annotations

import streamlit as st

from app.rag.pipeline import PipelineRun

STEPS_WITH_SEARCH = ["Question", "Embed", "Search knowledge base", "Select top matches", "Build context", "Ask Claude", "Answer"]
STEPS_DIRECT = ["Question", "Ask Claude", "Answer"]


def render_flow(run: PipelineRun | None) -> None:
    """Render the horizontal step flow. If `run` is None, shows the idle
    (not-yet-run) version."""
    steps = STEPS_WITH_SEARCH if (run is None or run.rag_enabled) else STEPS_DIRECT

    html_parts = ['<div class="flow">']
    for i, step in enumerate(steps):
        css_class = "flow-step"
        if run is not None:
            if run.error and step in ("Ask Claude", "Answer"):
                css_class += " skipped"
            elif run.below_threshold and step in ("Build context", "Ask Claude", "Answer"):
                css_class += " skipped"
            else:
                css_class += " done"
        html_parts.append(f'<div class="{css_class}">{step}</div>')
        if i < len(steps) - 1:
            html_parts.append('<div class="flow-arrow">&#8594;</div>')
    html_parts.append("</div>")

    st.markdown("".join(html_parts), unsafe_allow_html=True)


def render_stage_details(run: PipelineRun) -> None:
    """Expandable per-step detail panels shown below the flow diagram."""
    if run.rag_enabled:
        with st.expander("Search results"):
            if not run.retrieved:
                st.warning("No passages were retrieved. Has the knowledge base been indexed?")
            for i, r in enumerate(run.retrieved, start=1):
                st.markdown(f"**#{i}** `{r.chunk_id}` — match **{r.score:.2f}**")
            st.caption(f"Search took {run.timings.retrieval_ms:.0f} ms")

        if run.below_threshold:
            with st.expander("No sufficiently relevant context found", expanded=True):
                st.error(
                    f"Best match score: {run.best_score:.2f}\n\n"
                    f"Required threshold: {run.threshold:.2f}\n\n"
                    "The system declined to answer rather than guess."
                )
            return

        with st.expander("Exact request sent to Claude"):
            st.markdown("**Instructions**")
            st.markdown(f'<div class="mono-block">{run.system_prompt}</div>', unsafe_allow_html=True)
            st.markdown("**Context and question**")
            st.markdown(f'<div class="mono-block">{run.prompt}</div>', unsafe_allow_html=True)
            st.caption(f"Assembled in {run.timings.prompt_ms:.2f} ms")

    if run.error:
        st.error(
            "The request to Claude failed. Check the API key, model name, "
            "network connection, and available API credits."
        )
        with st.expander("Technical detail"):
            st.code(run.error)
        return

    if run.answer:
        with st.expander("Response", expanded=True):
            st.markdown(run.answer.text)
            cols = st.columns(4)
            cols[0].metric("Model", run.answer.model)
            cols[1].metric("Input tokens", run.answer.input_tokens or "—")
            cols[2].metric("Output tokens", run.answer.output_tokens or "—")
            cols[3].metric("Response time", f"{run.timings.claude_ms:.0f} ms")


def render_timing_summary(run: PipelineRun) -> None:
    st.markdown("**Timing**")
    rows = []
    if run.rag_enabled:
        rows.append(("Embedding", run.timings.embedding_ms))
        rows.append(("Search", run.timings.retrieval_ms))
        rows.append(("Context assembly", run.timings.prompt_ms))
    rows.append(("Claude response", run.timings.claude_ms))

    lines = [f"{name:<20}{ms:>8.1f} ms" for name, ms in rows]
    lines.append("-" * 28)
    lines.append(f"{'Total':<20}{run.timings.total_ms:>8.1f} ms")
    st.markdown(f'<div class="mono-block">{chr(10).join(lines)}</div>', unsafe_allow_html=True)
