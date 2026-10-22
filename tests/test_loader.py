import os
import tempfile

from app.rag.loader import load_markdown_files


def _write(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def test_loads_markdown_files():
    with tempfile.TemporaryDirectory() as tmp:
        _write(os.path.join(tmp, "a.md"), "# Title\n\nSome content here.")
        _write(os.path.join(tmp, "b.md"), "# Other\n\nMore content.")

        docs = load_markdown_files(tmp)

        assert len(docs) == 2
        sources = {d.metadata["source"] for d in docs}
        assert sources == {"a.md", "b.md"}


def test_ignores_empty_files():
    with tempfile.TemporaryDirectory() as tmp:
        _write(os.path.join(tmp, "empty.md"), "   \n\n  ")
        _write(os.path.join(tmp, "real.md"), "# Real\n\nContent.")

        docs = load_markdown_files(tmp)

        assert len(docs) == 1
        assert docs[0].metadata["source"] == "real.md"


def test_preserves_metadata_and_recurses_subdirectories():
    with tempfile.TemporaryDirectory() as tmp:
        _write(os.path.join(tmp, "sub", "nested.md"), "# Nested Heading\n\nBody text.")

        docs = load_markdown_files(tmp)

        assert len(docs) == 1
        doc = docs[0]
        assert doc.metadata["source"] == "nested.md"
        assert doc.metadata["path"] == "sub/nested.md"
        assert doc.metadata["heading"] == "Nested Heading"


def test_ignores_non_markdown_files():
    with tempfile.TemporaryDirectory() as tmp:
        _write(os.path.join(tmp, "notes.txt"), "should be ignored")
        _write(os.path.join(tmp, "doc.md"), "# Doc\n\ncontent")

        docs = load_markdown_files(tmp)

        assert len(docs) == 1
        assert docs[0].metadata["source"] == "doc.md"


def test_missing_directory_returns_empty_list():
    docs = load_markdown_files("/nonexistent/path/that/does/not/exist")
    assert docs == []
