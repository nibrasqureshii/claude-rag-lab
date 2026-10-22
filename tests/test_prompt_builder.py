from app.rag.prompt_builder import SYSTEM_PROMPT, build_prompt
from app.rag.retriever import RetrievalResult


def make_result(chunk_id, text, source, chunk_index, score=0.9):
    return RetrievalResult(
        chunk_id=chunk_id,
        text=text,
        score=score,
        metadata={"source": source, "chunk_index": chunk_index},
    )


def test_includes_question():
    prompt = build_prompt("What is the refund policy?", [])
    assert "What is the refund policy?" in prompt


def test_includes_retrieved_context():
    results = [make_result("refund-policy::chunk-003", "Customers may request a refund within 17 days.", "refund-policy.md", 3)]
    prompt = build_prompt("What is the refund policy?", results)
    assert "Customers may request a refund within 17 days." in prompt


def test_labels_sources():
    results = [make_result("refund-policy::chunk-003", "Some text.", "refund-policy.md", 3)]
    prompt = build_prompt("question", results)
    assert "[Source: refund-policy.md | chunk: 3]" in prompt


def test_includes_grounding_rules_in_system_prompt():
    assert "Use only the provided context" in SYSTEM_PROMPT
    assert "I don't have enough information in the knowledge base." in SYSTEM_PROMPT


def test_handles_no_retrieved_chunks():
    prompt = build_prompt("question with no context", [])
    assert "no relevant context retrieved" in prompt
