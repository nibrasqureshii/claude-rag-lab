# Retrieval: Top-K and Thresholds

Retrieval is the full "question → best matching chunks" pipeline:

```text
Question
   │
   ▼  embed the question (same model used for chunks)
Query Embedding
   │
   ▼  ask Chroma for the closest stored vectors
Vector Search
   │
   ▼  keep only the best N matches
Top-K Results
   │
   ▼  optionally drop anything below a similarity cutoff
Similarity Threshold
```

## Top-K

"K" is just how many chunks to retrieve. Top-3 means "give me the 3 closest
chunks." Top-10 means "give me the 10 closest chunks."

More chunks (**higher K**) can improve recall — you're less likely to miss
a relevant fact that happened to score slightly lower. But more chunks also
means more text competing for Claude's attention in the prompt, which can
dilute focus and occasionally introduce irrelevant tangents. Try this in
the app's **Experiments → Top-K** tab.

## Similarity threshold

A threshold is a minimum acceptable [[vector-search|similarity score]]. If
the *best* retrieved chunk still scores below the threshold, the system
concludes "nothing in the knowledge base is actually relevant to this
question" — and refuses to fabricate an answer instead of guessing.

This is what happens in **Experiments → Retrieval Failure** when you ask
something like *"What was Acme's revenue last year?"* — a question this
knowledge base was never given an answer to.

See [[hallucination]] for why this refusal matters.
