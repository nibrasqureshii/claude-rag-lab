"""
Stage 6 of the RAG pipeline: PROMPT CONSTRUCTION.

This is the "Augment" in "Retrieve, Augment, Generate": we take the
retrieved chunks and manually assemble them into the exact text prompt that
gets sent to Claude. Nothing here is hidden behind a framework — the string
this function returns is precisely what the model sees, and the UI displays
it verbatim in the Prompt Inspector.
"""

from __future__ import annotations

from app.rag.retriever import RetrievalResult

SYSTEM_PROMPT = (
    "You are answering questions using a private knowledge base.\n\n"
    "Rules:\n"
    "- Use only the provided context.\n"
    "- Do not invent facts not supported by the context.\n"
    "- If the answer is not present in the context, say: "
    '"I don\'t have enough information in the knowledge base."'
)


def build_prompt(question: str, retrieved_chunks: list[RetrievalResult]) -> str:
    """Assemble the final user-turn prompt sent to Claude.

    The system instructions (grounding rules) live separately in
    SYSTEM_PROMPT and are passed to the Claude client's `system` parameter.
    This function builds the CONTEXT + QUESTION block that becomes the
    user message.
    """
    context_blocks = []
    for chunk in retrieved_chunks:
        source = chunk.metadata.get("source", "unknown")
        chunk_index = chunk.metadata.get("chunk_index", "?")
        context_blocks.append(f"[Source: {source} | chunk: {chunk_index}]\n{chunk.text}")

    context_text = "\n\n".join(context_blocks) if context_blocks else "(no relevant context retrieved)"

    return f"CONTEXT\n\n{context_text}\n\nQUESTION\n\n{question}"
