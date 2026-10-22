from app.rag.chunker import chunk_document
from app.rag.loader import Document


def make_document(word_count: int, heading: str = "Heading") -> Document:
    words = " ".join(f"word{i}" for i in range(word_count))
    text = f"# {heading}\n\n{words}"
    return Document(text=text, metadata={"source": "test.md", "path": "test.md", "heading": heading})


def test_chunks_short_document_into_one_chunk():
    doc = make_document(100)
    chunks = chunk_document(doc, chunk_size=500, overlap=75)
    assert len(chunks) == 1
    assert chunks[0].chunk_index == 0


def test_respects_chunk_size():
    doc = make_document(1200)
    chunks = chunk_document(doc, chunk_size=500, overlap=75)
    for chunk in chunks:
        assert len(chunk.text.split()) <= 500


def test_creates_overlap_between_consecutive_chunks():
    doc = make_document(1000)
    chunks = chunk_document(doc, chunk_size=500, overlap=75)
    assert len(chunks) >= 2

    first_words = chunks[0].text.split()
    second_words = chunks[1].text.split()
    overlap_words = first_words[-75:]
    assert second_words[:75] == overlap_words


def test_preserves_metadata():
    doc = make_document(50, heading="Refund Policy")
    chunks = chunk_document(doc, chunk_size=500, overlap=75)

    chunk = chunks[0]
    assert chunk.source == "test.md"
    assert chunk.section == "Refund Policy"
    assert chunk.metadata["source"] == "test.md"
    assert chunk.metadata["chunk_index"] == 0
    assert chunk.chunk_id == "test::chunk-000"


def test_rejects_overlap_greater_than_or_equal_to_chunk_size():
    doc = make_document(100)
    try:
        chunk_document(doc, chunk_size=100, overlap=100)
        assert False, "expected ValueError"
    except ValueError:
        pass
