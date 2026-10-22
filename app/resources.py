"""
Streamlit resource caching.

Streamlit re-runs the whole script top-to-bottom on every user interaction
(every click, every slider drag). Without caching, that would reload the
~90MB embedding model and reopen the Chroma client dozens of times per
minute. `st.cache_resource` tells Streamlit "build this once per session
(or until code changes) and hand back the same object every time."
"""

from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

from app.rag.claude_client import ClaudeClient
from app.rag.embedder import Embedder
from app.rag.vector_store import VectorStore

CHROMA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "chroma")
KNOWLEDGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge")


@st.cache_resource(show_spinner="Loading embedding model (first run only)...")
def get_embedder() -> Embedder:
    return Embedder()


@st.cache_resource(show_spinner=False)
def get_vector_store(_embedder: Embedder) -> VectorStore:
    # Leading underscore on the param tells Streamlit's cache not to try
    # hashing the Embedder object itself.
    return VectorStore(persist_path=CHROMA_PATH, embedder=_embedder)


def load_environment() -> None:
    """Load ANTHROPIC_API_KEY / ANTHROPIC_MODEL from a local .env file."""
    load_dotenv()


def get_claude_client_safe() -> ClaudeClient | None:
    """Return a ClaudeClient, or None if configuration is missing.

    We don't cache this one with st.cache_resource because we want a fresh
    config check (e.g. was .env just fixed?) without requiring a full app
    restart -- construction is cheap since it's just an SDK client, not a
    loaded model.
    """
    try:
        return ClaudeClient()
    except Exception:
        return None
