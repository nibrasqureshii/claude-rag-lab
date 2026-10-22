from app.rag.retriever import retrieve


class FakeEmbedder:
    """Deterministic stand-in for the real sentence-transformers Embedder,
    so retriever tests don't need to download/load any model."""

    def embed_query(self, text):
        return [1.0, 0.0]


class FakeVectorStore:
    """Deterministic stand-in for VectorStore.query(), so retriever tests
    don't need a real Chroma collection."""

    def __init__(self, distances):
        self._distances = distances

    def query(self, query_vector, top_k=5):
        n = min(top_k, len(self._distances))
        ids = [f"doc::chunk-{i:03d}" for i in range(n)]
        documents = [f"text {i}" for i in range(n)]
        metadatas = [{"source": "doc.md", "chunk_index": i} for i in range(n)]
        distances = self._distances[:n]
        return {
            "ids": [ids],
            "documents": [documents],
            "metadatas": [metadatas],
            "distances": [distances],
        }


def test_returns_top_k_results():
    store = FakeVectorStore(distances=[0.1, 0.2, 0.3, 0.4, 0.5])
    results = retrieve("query", store, FakeEmbedder(), top_k=3)
    assert len(results) == 3


def test_results_ordered_by_score_descending():
    # Lower distance -> higher similarity, so ids should come back in the
    # same order here since distances are already ascending (nearest first).
    store = FakeVectorStore(distances=[0.1, 0.3, 0.2])
    results = retrieve("query", store, FakeEmbedder(), top_k=3)
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_similarity_threshold_filters_low_scores():
    # distance 0.1 -> similarity ~0.909, distance 5.0 -> similarity ~0.167
    store = FakeVectorStore(distances=[0.1, 5.0])
    results = retrieve("query", store, FakeEmbedder(), top_k=2, similarity_threshold=0.5)
    assert len(results) == 1
    assert results[0].score >= 0.5


def test_no_threshold_returns_everything_within_top_k():
    store = FakeVectorStore(distances=[0.1, 5.0])
    results = retrieve("query", store, FakeEmbedder(), top_k=2, similarity_threshold=None)
    assert len(results) == 2
