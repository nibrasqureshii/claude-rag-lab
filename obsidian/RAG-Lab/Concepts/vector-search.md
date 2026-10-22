# Vector (Similarity) Search

Vector search finds the stored [[embeddings|embedding]] vectors that are
**closest** to a query vector, in the mathematical sense of "distance
between points in space."

```text
Query: "Can I get my money back?"
   │
   ▼  embed
[0.09, -0.51, 0.77, ...]
   │
   ▼  compare against every stored chunk vector
refund-policy::chunk-000   distance 0.09   → similarity 0.92
company::chunk-002         distance 0.61   → similarity 0.62
engineering::chunk-001     distance 1.40   → similarity 0.42
```

This project uses **ChromaDB**, running entirely locally, to store chunk
vectors and answer "which vectors are closest to this one?" queries
efficiently — Chroma does not read, summarize, or generate anything. It is
a search index over numbers, nothing more.

## Similarity is not confidence

The score shown in the app (e.g. `0.91`) is a normalized closeness measure,
not a probability and not a measure of how "confident" the system is that
the answer is correct. Two pieces of text can have a high similarity score
because they discuss the same topic, even if one of them doesn't actually
answer the question. See [[retrieval]] for how a similarity threshold is
used to guard against this.

## Does Claude search the vector database?

**No.** This is one of the most common misconceptions about RAG. Claude
never touches Chroma directly. Your own Python code runs the vector search,
picks the best chunks, and only *then* hands them to Claude as plain text
inside a prompt. See [[RAG]].
