"""
Stage 1 of the RAG pipeline: LOADING.

This module turns Markdown files sitting on disk into plain Python objects
(`Document`) that the rest of the pipeline can work with. It knows nothing
about chunking, embeddings, or Claude — its only job is "read files, keep
useful metadata."
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class Document:
    """A single loaded source document, before it is split into chunks."""

    text: str
    metadata: dict = field(default_factory=dict)


def _first_heading(text: str) -> str | None:
    """Return the first Markdown heading in the text, if any.

    We keep this intentionally naive (no full Markdown parser) because the
    teaching goal here is "preserve headings where practical", not build a
    Markdown engine.
    """
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return None


def load_markdown_files(directory: str) -> list[Document]:
    """Recursively load every .md file under `directory` into Documents.

    Behavior (matches the lab spec):
    - Recurses into subdirectories.
    - Skips empty files (after whitespace stripping).
    - Skips files that can't be read (bad encoding, permissions, etc.)
      instead of crashing the whole app.
    - Preserves the filename, the relative path, and the first heading.
    """
    documents: list[Document] = []

    if not os.path.isdir(directory):
        return documents

    for root, _dirs, files in os.walk(directory):
        for filename in sorted(files):
            if not filename.lower().endswith(".md"):
                continue

            full_path = os.path.join(root, filename)
            rel_path = os.path.relpath(full_path, directory)

            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    text = f.read()
            except (OSError, UnicodeDecodeError):
                # A single unreadable file should not take down ingestion.
                continue

            if not text.strip():
                continue

            documents.append(
                Document(
                    text=text,
                    metadata={
                        "source": filename,
                        "path": rel_path.replace(os.sep, "/"),
                        "heading": _first_heading(text),
                    },
                )
            )

    return documents
