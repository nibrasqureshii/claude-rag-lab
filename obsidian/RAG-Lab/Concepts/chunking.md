# Chunking

A document gets divided into smaller units, called **chunks**, before it is
ever turned into an embedding.

## Why not just embed the whole document?

Because [[vector-search]] compares *one vector* against *one query vector*.
If you embedded an entire 5-page document as a single vector, that vector
would represent the "average meaning" of the whole document — refund
policy, support hours, and unrelated trivia, all blended together.

A very specific question like "how many days do I have for a refund?"
would then have to compete against that blended average, and you would have
no way to tell the user *which paragraph* the answer actually came from.

Chunking fixes this by making the retrievable unit small and specific
enough that its embedding reflects one focused idea.

## The trade-off

- **Smaller chunks** → more precise retrieval, but might cut a fact off
  from the surrounding sentence that gives it context.
- **Larger chunks** → more surrounding context per chunk, but the
  embedding becomes a blend of more ideas, which can hurt precision.
- **Overlap** between consecutive chunks helps prevent an important
  sentence from being awkwardly split exactly at a chunk boundary.

Try this yourself in the app's **Experiments → Chunk Size** tab: re-index
with a small chunk size, then a large one, and watch how the retrieved
results change for the same question.

## What gets stored with each chunk

- The source document filename
- The section/heading it came from, if available
- A stable chunk ID like `refund-policy::chunk-003`
- The chunk index within its document

This metadata is what powers source citations later — see
[[prompt-construction]].
