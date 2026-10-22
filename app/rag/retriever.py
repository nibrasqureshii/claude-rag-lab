"""
Stage 5 of the RAG pipeline: RETRIEVAL.

This is where "Question" becomes "Top-K relevant chunks". The retriever
embeds the user's question with the SAME embedding model used for the
documents, asks the vector store for the closest matches, and normalizes
Chroma's raw distance numbers into an intuitive 0-to-1 "similarity" score.

Important teaching note (see also prompt_builder.py and the Retrieval tab):
this similarity score is NOT a probability and NOT a confidence percentage.
It only tells you how close two vectors are in embedding space.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.rag.embedder import Embedder
from app.rag.vector_store import VectorStore


@dataclass
class RetrievalResult:
    """One retrieved chunk, ready for display and prompt-building."""

    chunk_id: str
    text: str
    score: float
    metadata: dict


def _distance_to_similarity(distance: float) -> float:
    """Convert a Chroma L2 distance into a 0-1 "similarity" for display.

    Chroma's default distance is squared L2 (smaller = more similar, with a
    lower bound of 0 and no fixed upper bound). We map it into (0, 1] with
    a simple decay so the UI can show something like "0.91" instead of a
    raw distance like "0.14", which is much easier for a junior to reason
    about. This is a display convenience, not a statistically calibrated
    probability.
    """
    return 1.0 / (1.0 + distance)


def retrieve(
    query: str,
    vector_store: VectorStore,
    embedder: Embedder,
    top_k: int = 5,
    similarity_threshold: float | None = None,
) -> list[RetrievalResult]:
    """Run the full retrieval pipeline for one question.

    Pipeline: Question -> Query Embedding -> Vector Search -> Top K ->
    optional similarity threshold filter.
    """
    query_vector = embedder.embed_query(query)
    raw = vector_store.query(query_vector, top_k=top_k)

    ids = raw["ids"][0]
    documents = raw["documents"][0]
    metadatas = raw["metadatas"][0]
    distances = raw["distances"][0]

    results = [
        RetrievalResult(
            chunk_id=chunk_id,
            text=text,
            score=_distance_to_similarity(distance),
            metadata=metadata,
        )
        for chunk_id, text, metadata, distance in zip(ids, documents, metadatas, distances)
    ]

    # Chroma already returns nearest-first, but we sort explicitly so the
    # ordering guarantee doesn't silently depend on an implementation detail.
    results.sort(key=lambda r: r.score, reverse=True)

    if similarity_threshold is not None:
        results = [r for r in results if r.score >= similarity_threshold]

    return results
