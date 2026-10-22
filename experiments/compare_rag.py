"""
Standalone script: asks the same question with and without RAG, and prints
both answers side by side in the terminal. Requires ANTHROPIC_API_KEY to be
set (loaded from .env). Run with:

    python experiments/compare_rag.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

from app.rag.chunker import chunk_documents
from app.rag.claude_client import ClaudeClient
from app.rag.embedder import Embedder
from app.rag.loader import load_markdown_files
from app.rag.pipeline import run_direct_pipeline, run_rag_pipeline
from app.rag.vector_store import VectorStore

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KNOWLEDGE_DIR = os.path.join(BASE_DIR, "knowledge")
CHROMA_PATH = os.path.join(BASE_DIR, "data", "chroma_experiment")

QUESTION = "What services does Acme offer?"


def main():
    load_dotenv()

    print("Loading embedding model...")
    embedder = Embedder()
    store = VectorStore(persist_path=CHROMA_PATH, embedder=embedder)

    print("Indexing knowledge base...")
    documents = load_markdown_files(KNOWLEDGE_DIR)
    chunks = chunk_documents(documents, chunk_size=500, overlap=75)
    store.reset()
    store.index_documents(chunks)

    claude = ClaudeClient()

    print(f"\nQuestion: {QUESTION}\n")

    print("=" * 60)
    print("WITHOUT RAG")
    print("=" * 60)
    off = run_direct_pipeline(QUESTION, claude)
    print(off.answer.text if off.answer else f"ERROR: {off.error}")

    print()
    print("=" * 60)
    print("WITH RAG")
    print("=" * 60)
    on = run_rag_pipeline(QUESTION, store, embedder, claude, top_k=5, similarity_threshold=0.35)
    if on.below_threshold:
        print(f"No relevant context found (best similarity {on.best_score:.2f}).")
    elif on.answer:
        print(on.answer.text)
        print(f"\nSources: {sorted({r.metadata.get('source') for r in on.included_results})}")
    else:
        print(f"ERROR: {on.error}")


if __name__ == "__main__":
    main()
