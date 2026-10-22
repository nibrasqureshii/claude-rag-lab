"""
Acme Knowledge Assistant — entrypoint.

Run with:
    streamlit run app/main.py

This file only wires together navigation and shared resources. All actual
pipeline logic lives in app/rag/*, and each tab's rendering lives in
app/ui/*.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

from app import resources, styles
from app.rag.chunker import chunk_documents
from app.rag.loader import load_markdown_files
from app.rag.pipeline import run_direct_pipeline, run_rag_pipeline
from app.rag.retriever import retrieve
from app.ui import chat, pipeline_view, retrieval_view

st.set_page_config(page_title="Acme Knowledge Assistant", layout="wide")
styles.inject()
resources.load_environment()

st.markdown(
    """
<div class="app-header">
  <p class="app-title">Acme Knowledge Assistant</p>
  <p class="app-subtitle">Ask questions and see exactly where each answer comes from.</p>
</div>
""",
    unsafe_allow_html=True,
)

embedder = resources.get_embedder()
vector_store = resources.get_vector_store(embedder)
claude_client = resources.get_claude_client_safe()

if claude_client is None:
    st.warning(
        "Claude API key is missing. Add ANTHROPIC_API_KEY to your .env file "
        "to enable answers. Search still works without it."
    )

with st.sidebar:
    st.markdown("### Search settings")
    st.session_state.setdefault("top_k", 5)
    st.session_state.setdefault("similarity_threshold", 0.35)
    st.session_state["top_k"] = st.slider(
        "Results to retrieve",
        1, 10, st.session_state["top_k"],
        help=(
            "How many passages to pull from the knowledge base for each question. "
            "More results can surface facts a narrower search would miss, but also "
            "add more text for Claude to sort through, which can dilute focus."
        ),
    )
    st.session_state["similarity_threshold"] = st.slider(
        "Relevance threshold",
        0.0, 1.0, st.session_state["similarity_threshold"], 0.01,
        help=(
            "The minimum match score a search result must reach before the "
            "assistant will trust it. If nothing found clears this bar, the "
            "assistant says it doesn't have enough information instead of "
            "guessing. Raise it to be stricter, lower it to be more lenient."
        ),
    )
    st.markdown("---")
    st.markdown("### Knowledge base")
    st.metric("Passages indexed", vector_store.count())
    if vector_store.count() == 0:
        st.warning("The knowledge base is empty. Go to the Knowledge Base tab and index the documents.")

tab_ask, tab_compare, tab_kb = st.tabs(["Ask", "Compare", "Knowledge Base"])

with tab_ask:
    chat.render(vector_store, embedder, claude_client)

with tab_compare:
    st.markdown("### Compare answers")
    st.caption("Ask the same question with and without the knowledge base to see the difference.")

    compare_question = st.text_input(
        "Question",
        value="What services does Acme offer?",
        key="compare_question",
    )

    if st.button("Compare", type="primary"):
        if claude_client is None:
            st.error("Claude API key is missing. Add ANTHROPIC_API_KEY to your .env file.")
        else:
            col_off, col_on = st.columns(2)
            with col_off:
                st.markdown("#### Without knowledge base")
                with st.spinner("Asking Claude..."):
                    run_off = run_direct_pipeline(compare_question, claude_client)
                pipeline_view.render_flow(run_off)
                if run_off.answer:
                    st.write(run_off.answer.text)
                elif run_off.error:
                    st.error("The request to Claude failed.")

            with col_on:
                st.markdown("#### With knowledge base")
                with st.spinner("Searching and asking Claude..."):
                    run_on = run_rag_pipeline(
                        compare_question, vector_store, embedder, claude_client,
                        top_k=st.session_state["top_k"],
                        similarity_threshold=st.session_state["similarity_threshold"],
                    )
                pipeline_view.render_flow(run_on)
                if run_on.below_threshold:
                    st.warning("No sufficiently relevant context was found above the threshold.")
                elif run_on.answer:
                    st.write(run_on.answer.text)
                elif run_on.error:
                    st.error("The request to Claude failed.")

            st.caption(
                "The answer without the knowledge base makes no claim of private knowledge. "
                "The answer with the knowledge base is grounded in a cited source document."
            )

    st.markdown("---")
    last_run = st.session_state.get("last_run")
    if last_run:
        st.markdown("#### Most recent question from the Ask tab")
        pipeline_view.render_flow(last_run)
        pipeline_view.render_stage_details(last_run)
    else:
        st.info("Ask a question in the Ask tab, or run a comparison above.")

with tab_kb:
    st.markdown("### Knowledge base")

    documents = load_markdown_files(resources.KNOWLEDGE_DIR)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Documents", len(documents))
    col2.metric("Passages indexed", vector_store.count())
    col3.metric("Vector dimensions", embedder.dimensions)
    col4.metric("Collection", vector_store.collection_name)

    st.markdown("#### Documents")
    for doc in documents:
        word_count = len(doc.text.split())
        st.markdown(f"- `{doc.metadata['source']}` — {word_count} words")

    st.markdown("---")
    st.markdown("#### Indexing settings")
    st.caption(
        "Controls how source documents are split into searchable passages before "
        "indexing. Changing these requires re-indexing to take effect."
    )

    col_size, col_overlap = st.columns(2)
    chunk_size = col_size.select_slider(
        "Passage size (words)",
        options=[150, 300, 500, 750, 1000],
        value=st.session_state.get("chunk_size", 500),
        help=(
            "How many words go into each searchable passage. Smaller passages are "
            "more precise but can lose surrounding context; larger passages keep "
            "more context but can blend multiple ideas into one search result."
        ),
    )
    overlap = col_overlap.select_slider(
        "Passage overlap (words)",
        options=[0, 25, 50, 75, 100],
        value=st.session_state.get("overlap", 75),
        help=(
            "How many words consecutive passages share at their boundary. Overlap "
            "reduces the chance that a relevant sentence gets split across two "
            "passages and missed by search."
        ),
    )

    if overlap >= chunk_size:
        st.error("Passage overlap must be smaller than passage size.")
    else:
        st.session_state["chunk_size"] = chunk_size
        st.session_state["overlap"] = overlap

        col_reindex, col_reset = st.columns(2)

        if col_reindex.button("Re-index with these settings", use_container_width=True, type="primary"):
            old_count = vector_store.count()
            with st.spinner("Loading documents..."):
                documents = load_markdown_files(resources.KNOWLEDGE_DIR)
            with st.spinner(f"Splitting into passages ({chunk_size} words, {overlap} overlap)..."):
                chunks = chunk_documents(documents, chunk_size=chunk_size, overlap=overlap)
            with st.spinner(f"Indexing {len(chunks)} passages..."):
                vector_store.reset()
                vector_store.index_documents(chunks)
            st.success(
                f"Indexing complete. {len(chunks)} passages, "
                f"{embedder.dimensions} dimensions each. "
                f"({old_count} → {vector_store.count()} passages)"
            )

        if col_reset.button("Clear index", use_container_width=True):
            vector_store.reset()
            st.success("Index cleared. Re-index to rebuild it.")

    st.markdown("---")
    st.markdown("#### Search the knowledge base directly")
    st.caption("Search without generating an answer, to see what the retrieval step alone returns.")
    query = st.text_input("Search query", value="What does Acme do?", key="kb_search_query")
    if st.button("Search", key="kb_search_button"):
        top_k = st.session_state.get("top_k", 5)
        results = retrieve(query, vector_store, embedder, top_k=top_k)
        retrieval_view.render_semantic_search_results(results)

st.markdown("---")
st.caption("Acme Knowledge Assistant")
