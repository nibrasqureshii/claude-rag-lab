"""The Ask tab: the main entry point. Two ways to ask -- with the knowledge
base (grounded in indexed documents) or without it (Claude's general
knowledge only) -- so the difference is visible on every question, not just
in a separate comparison view.
"""

from __future__ import annotations

import streamlit as st

from app.rag.pipeline import run_direct_pipeline, run_rag_pipeline
from app.ui import pipeline_view, retrieval_view

EXAMPLE_QUESTIONS = [
    "What services does Acme offer?",
    "Where is Acme headquartered?",
    "What industries does Acme serve?",
    "What was Acme's revenue last year?",
]


def render(vector_store, embedder, claude_client) -> None:
    st.markdown("### Ask a question")
    st.caption(
        "Ask about Acme Software Co.. Compare an answer grounded "
        "in the knowledge base with one from Claude's general knowledge alone."
    )

    cols = st.columns(4)
    for i, q in enumerate(EXAMPLE_QUESTIONS):
        if cols[i].button(q, key=f"example_{i}", use_container_width=True):
            st.session_state["chat_question"] = q

    question = st.text_input(
        "Your question",
        value=st.session_state.get("chat_question", ""),
        placeholder="What services does Acme offer?",
        key="chat_question_input",
    )

    top_k = st.session_state.get("top_k", 5)
    threshold = st.session_state.get("similarity_threshold", 0.35)

    col_a, col_b = st.columns(2)
    run_rag = col_a.button("Answer using knowledge base", type="primary", use_container_width=True)
    run_direct = col_b.button("Answer without knowledge base", use_container_width=True)

    if not (run_rag or run_direct):
        pipeline_view.render_flow(None)
        st.info("Enter a question above and choose how to answer it.")
        return

    if not question.strip():
        st.warning("Please enter a question first.")
        return

    if claude_client is None:
        st.error("Claude API key is missing. Add ANTHROPIC_API_KEY to your .env file.")
        return

    if run_rag:
        with st.spinner("Searching the knowledge base and asking Claude..."):
            run = run_rag_pipeline(
                question, vector_store, embedder, claude_client,
                top_k=top_k, similarity_threshold=threshold,
            )
        st.session_state["last_run"] = run
    else:
        with st.spinner("Asking Claude..."):
            run = run_direct_pipeline(question, claude_client)
        st.session_state["last_run"] = run

    st.markdown("---")
    pipeline_view.render_flow(run)

    if run.rag_enabled:
        st.markdown("#### Retrieved context")
        st.caption(f"{len(run.retrieved)} passage(s) retrieved from the knowledge base.")
        retrieval_view.render_results(run.retrieved)

    pipeline_view.render_stage_details(run)

    if run.answer and not run.error and not run.below_threshold:
        st.markdown("#### Sources")
        sources = sorted({r.metadata.get("source", "unknown") for r in run.included_results}) if run.rag_enabled else []
        if sources:
            st.write(", ".join(f"`{s}`" for s in sources))
        else:
            st.caption("No knowledge base sources used — this answer came from Claude's general knowledge only.")

        pipeline_view.render_timing_summary(run)

        with st.expander("Why did Claude say this?"):
            _render_explanation(run)


def _render_explanation(run) -> None:
    if not run.rag_enabled:
        st.write(
            "The knowledge base was not used for this answer. Claude answered "
            "from its own general training knowledge, with no access to Acme's "
            "private documents. Any specific-sounding facts about Acme here "
            "are not grounded in real documents."
        )
        return

    sources = sorted({r.metadata.get("source", "unknown") for r in run.included_results})
    st.markdown("**Retrieved from:**")
    for s in sources:
        st.markdown(f"- {s}")

    st.markdown("**Passages included in the request:**")
    for r in run.included_results:
        st.markdown(f"- `{r.chunk_id}`")

    st.markdown("**Claude model:**")
    st.code(run.answer.model if run.answer else "unknown")

    st.info(
        "The knowledge base search supplied the private information. "
        "Claude's job was only to phrase an answer from the context it was given — "
        "this explanation is derived directly from that request, not a second "
        "question asked to Claude."
    )
