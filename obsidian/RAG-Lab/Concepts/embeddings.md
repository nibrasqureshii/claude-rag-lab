# Embeddings

An embedding turns **text → a numerical vector representing semantic
meaning.**

```text
"How long do I have to request a refund?"
        │
        ▼
[0.12, -0.42, 0.83, 0.05, ... ]   (384 numbers, in this project)
```

Two pieces of text that "mean" similar things end up with vectors that
point in similar directions in this 384-dimensional space, even if they
don't share any of the same words. That's the whole trick behind
[[vector-search]]: instead of matching keywords, we compare *meaning*.

## Why 384 numbers specifically?

This project uses a local, free model called
`sentence-transformers/all-MiniLM-L6-v2`. It happens to output 384-number
vectors. A different embedding model might output 768, 1024, or some other
size — the number itself isn't meaningful, it's just how much "room" that
particular model uses to represent meaning.

## Important: this runs locally

Generating embeddings does **not** call any paid API in this project. It
runs entirely on your own machine via `sentence-transformers`. The only
paid API call in the whole system is the final Claude answer — see
[[RAG]].

## Where this happens in the pipeline

Embeddings are created twice:

1. Once per chunk, when you index the knowledge base (see [[chunking]]).
2. Once per question, at query time — this is called the "query
   embedding," and it's what gets compared against every stored chunk
   vector during [[vector-search]].
