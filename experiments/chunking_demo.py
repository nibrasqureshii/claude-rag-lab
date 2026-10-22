"""
Standalone script: shows how chunk size and overlap change the number and
shape of chunks produced from the sample knowledge base. Run with:

    python experiments/chunking_demo.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.rag.chunker import chunk_documents
from app.rag.loader import load_markdown_files

KNOWLEDGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge")

SETTINGS = [
    (150, 25),
    (300, 50),
    (500, 75),
    (750, 100),
    (1000, 100),
]


def main():
    documents = load_markdown_files(KNOWLEDGE_DIR)
    print(f"Loaded {len(documents)} documents from {KNOWLEDGE_DIR}\n")

    for chunk_size, overlap in SETTINGS:
        chunks = chunk_documents(documents, chunk_size=chunk_size, overlap=overlap)
        avg_words = sum(len(c.text.split()) for c in chunks) / len(chunks) if chunks else 0
        print(
            f"chunk_size={chunk_size:>5}  overlap={overlap:>4}  "
            f"-> {len(chunks):>3} chunks  (avg {avg_words:.0f} words/chunk)"
        )


if __name__ == "__main__":
    main()
