"""
Stage 2 of the RAG pipeline: CHUNKING.

Why chunk at all? A vector database searches over *chunks*, not whole
documents. If we embedded an entire document as one vector, a search for a
very specific fact (like "how many days for a refund?") would have to
compete against the "average meaning" of a huge document, and we could not
tell the user which paragraph the answer actually came from.

This chunker is deliberately simple: it splits on whitespace-separated words
rather than using a real tokenizer. That keeps the teaching demo dependency
list small while still being close enough to "500 tokens" for the point we
are making: chunk size and overlap change what gets retrieved.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.rag.loader import Document


@dataclass
class Chunk:
    """A single retrievable slice of a source document."""

    chunk_id: str
    text: str
    source: str
    chunk_index: int
    section: str | None = None
    metadata: dict = field(default_factory=dict)


def _split_into_sections(text: str) -> list[tuple[str | None, str]]:
    """Split text into (heading, body) pairs at each Markdown heading line.

    Text before the first heading is kept under a `None` heading so it is
    never silently dropped.
    """
    lines = text.splitlines()
    sections: list[tuple[str | None, list[str]]] = []
    current_heading: str | None = None
    current_lines: list[str] = []

    heading_pattern = re.compile(r"^\s{0,3}#{1,6}\s+(.*)$")

    for line in lines:
        match = heading_pattern.match(line)
        if match:
            if current_lines:
                sections.append((current_heading, current_lines))
            current_heading = match.group(1).strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        sections.append((current_heading, current_lines))

    return [(heading, "\n".join(body_lines)) for heading, body_lines in sections]


def chunk_document(
    document: Document,
    chunk_size: int = 500,
    overlap: int = 75,
) -> list[Chunk]:
    """Split one Document into overlapping word-based Chunks.

    `chunk_size` and `overlap` are counted in words, not tokens or
    characters — a pragmatic simplification for an educational demo. Each
    chunk keeps track of which section (heading) it came from, so the UI can
    show source + section together.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0:
        raise ValueError("overlap cannot be negative")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    source = document.metadata.get("source", "unknown")
    source_slug = re.sub(r"\.md$", "", source, flags=re.IGNORECASE)

    chunks: list[Chunk] = []
    chunk_index = 0
    step = chunk_size - overlap

    for heading, body in _split_into_sections(document.text):
        words = body.split()
        if not words:
            continue

        start = 0
        while start < len(words):
            piece_words = words[start : start + chunk_size]
            chunk_text = " ".join(piece_words)

            chunk_id = f"{source_slug}::chunk-{chunk_index:03d}"
            chunks.append(
                Chunk(
                    chunk_id=chunk_id,
                    text=chunk_text,
                    source=source,
                    chunk_index=chunk_index,
                    section=heading,
                    metadata={
                        "source": source,
                        "path": document.metadata.get("path") or "",
                        "chunk_id": chunk_id,
                        "chunk_index": chunk_index,
                        "section": heading or "",
                    },
                )
            )
            chunk_index += 1

            if start + chunk_size >= len(words):
                break
            start += step

    return chunks


def chunk_documents(
    documents: list[Document],
    chunk_size: int = 500,
    overlap: int = 75,
) -> list[Chunk]:
    """Convenience helper: chunk a whole list of Documents at once."""
    all_chunks: list[Chunk] = []
    for document in documents:
        all_chunks.extend(chunk_document(document, chunk_size=chunk_size, overlap=overlap))
    return all_chunks
