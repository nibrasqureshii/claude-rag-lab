"""
Standalone script: index the knowledge base and run a few sample queries,
printing retrieved chunks and similarity scores to the terminal. Run with:

    python experiments/retrieval_demo.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.rag.chunker import chunk_documents
from app.rag.embedder import Embedder
from app.rag.loader import load_markdown_files
from app.rag.retriever import retrieve
from app.rag.vector_store import VectorStore

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KNOWLEDGE_DIR = os.path.join(BASE_DIR, "knowledge")
CHROMA_PATH = os.path.join(BASE_DIR, "data", "chroma_experiment")

QUESTIONS = [
    "What services does Acme offer?",
    "Where is Acme headquartered?",
    "What industries does Acme serve?",
    "What was Acme's revenue last year?",
]


def main():
    print("Loading embedding model...")
    embedder = Embedder()
    store = VectorStore(persist_path=CHROMA_PATH, embedder=embedder)

    print("Indexing knowledge base...")
    documents = load_markdown_files(KNOWLEDGE_DIR)
    chunks = chunk_documents(documents, chunk_size=500, overlap=75)
    store.reset()
    store.index_documents(chunks)
    print(f"Indexed {store.count()} chunks.\n")

    for question in QUESTIONS:
        print(f"Q: {question}")
        results = retrieve(question, store, embedder, top_k=3)
        for r in results:
            print(f"    {r.score:.2f}  {r.metadata.get('source')}  {r.chunk_id}")
        print()


if __name__ == "__main__":
    main()
