"""
Stage 4 of the RAG pipeline: the VECTOR STORE.

This wraps ChromaDB, a local vector database. Chroma's only job here is:
store vectors + their text/metadata, and later find the vectors closest to
a query vector. Chroma does NOT read, understand, or generate anything —
it is a similarity search index, nothing more.

Keeping this wrapper thin and explicit matters for the teaching goal: a
junior should be able to see exactly what "the vector database" does versus
what "the LLM" does.
"""

from __future__ import annotations

import chromadb

from app.rag.chunker import Chunk
from app.rag.embedder import Embedder

COLLECTION_NAME = "knowledge"


class VectorStore:
    """A thin wrapper around a local, persistent Chroma collection."""

    def __init__(self, persist_path: str, embedder: Embedder, collection_name: str = COLLECTION_NAME):
        self.persist_path = persist_path
        self.embedder = embedder
        self.collection_name = collection_name
        self._client = chromadb.PersistentClient(path=persist_path)
        self._collection = self._client.get_or_create_collection(name=collection_name)

    def reset(self) -> None:
        """Delete and recreate the collection, wiping all indexed chunks."""
        self._client.delete_collection(name=self.collection_name)
        self._collection = self._client.get_or_create_collection(name=self.collection_name)

    def count(self) -> int:
        """Number of chunks currently stored in the collection."""
        return self._collection.count()

    def index_documents(self, chunks: list[Chunk]) -> int:
        """Embed and store a list of chunks. Returns the number stored.

        Chunk IDs are stable (e.g. "refund-policy::chunk-003"), so
        re-indexing the same chunk twice overwrites it (via Chroma's
        `upsert`) instead of creating duplicates.
        """
        if not chunks:
            return 0

        texts = [chunk.text for chunk in chunks]
        vectors = self.embedder.embed_documents(texts)
        ids = [chunk.chunk_id for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]

        self._collection.upsert(
            ids=ids,
            embeddings=vectors,
            documents=texts,
            metadatas=metadatas,
        )
        return len(chunks)

    def query(self, query_vector: list[float], top_k: int = 5) -> dict:
        """Run a raw similarity search and return Chroma's native result
        shape. Most callers should use `retriever.retrieve()` instead,
        which wraps this into a friendlier `RetrievalResult` list."""
        if self.count() == 0:
            return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

        n_results = min(top_k, self.count())
        return self._collection.query(
            query_embeddings=[query_vector],
            n_results=n_results,
        )
