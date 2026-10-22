"""Renders retrieved source passages as cards: rank, source document,
section, match score, and full text. Nothing here calls Claude -- this view
exists to make retrieval visible as its own step, separate from generation.
"""

from __future__ import annotations

import streamlit as st

from app.rag.retriever import RetrievalResult


def _score_pill_class(score: float) -> str:
    if score >= 0.75:
        return "pill-green"
    if score >= 0.5:
        return "pill-amber"
    return "pill-red"


def render_results(results: list[RetrievalResult], title: str = "Retrieved passages") -> None:
    st.markdown(f"**{title}**")

    if not results:
        st.caption("No passages retrieved yet.")
        return

    for i, r in enumerate(results, start=1):
        source = r.metadata.get("source", "unknown")
        section = r.metadata.get("section") or "—"
        pill_class = _score_pill_class(r.score)

        st.markdown(
            f"""
<div class="source-card">
  <span class="status-pill pill-blue">#{i}</span>
  <span class="status-pill pill-gray">{source}</span>
  <span class="status-pill {pill_class}">match {r.score:.2f}</span>
</div>
""",
            unsafe_allow_html=True,
        )
        with st.expander(f"{section} — {r.chunk_id}"):
            st.write(r.text)

    st.caption(
        "Match score reflects how close a passage is to the question in meaning. "
        "It is not a confidence percentage."
    )


def render_semantic_search_results(results: list[RetrievalResult]) -> None:
    """Compact one-line-per-result view for the search-only mode."""
    if not results:
        st.caption("No matches found.")
        return
    for r in results:
        source = r.metadata.get("source", "unknown")
        st.markdown(f"**{r.score:.2f}**&nbsp;&nbsp;`{source}` — {r.text[:120]}...")
