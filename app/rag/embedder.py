"""
Stage 3 of the RAG pipeline: EMBEDDINGS.

An embedding turns text into a list of numbers (a vector) that captures
semantic meaning. Two chunks of text that "mean" similar things end up with
vectors that point in similar directions, which is what lets us do
similarity search later.

This runs entirely locally via `sentence-transformers` — no API key, no
network call, no cost. That is a deliberate teaching choice: the ONLY paid
service in this whole project is the Claude API call that generates the
final answer.
"""

from __future__ import annotations

from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class Embedder:
    """Wraps a local sentence-transformers model for embedding text."""

    def __init__(self, model_name: str = MODEL_NAME):
        self.model_name = model_name
        # Loading the model reads weights from disk/cache and is the slow
        # part of startup. Callers should construct one Embedder and reuse
        # it (see get_embedder() below for a Streamlit-cached singleton).
        self._model = SentenceTransformer(model_name)

    @property
    def dimensions(self) -> int:
        """The size of each embedding vector, read from the model itself
        rather than hard-coded, since different models produce different
        vector sizes."""
        return self._model.get_sentence_embedding_dimension()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of chunk texts for storage in the vector store."""
        vectors = self._model.encode(texts, show_progress_bar=False)
        return [vector.tolist() for vector in vectors]

    def embed_query(self, text: str) -> list[float]:
        """Embed a single user question at query time."""
        vector = self._model.encode([text], show_progress_bar=False)[0]
        return vector.tolist()


_cached_embedder: Embedder | None = None


def get_embedder() -> Embedder:
    """Return a process-wide singleton Embedder.

    Loading the sentence-transformers model takes real time (and CPU/RAM),
    so we only want to do it once per process. Streamlit's own
    `@st.cache_resource` is used on top of this in the UI layer, but this
    module-level cache also protects non-Streamlit callers (tests,
    experiments scripts).
    """
    global _cached_embedder
    if _cached_embedder is None:
        _cached_embedder = Embedder()
    return _cached_embedder
