# Claude RAG Lab — Workshop Presentation Outline

~12–14 slides, designed to be interactive rather than a text-heavy lecture.
Pair each slide with a live moment in the Streamlit app — don't just talk
about RAG, click through it.

---

### Slide 1 — Claude Knows A Lot — But Not Your Private Data

**Visual:** Claude icon with a "knowledge cutoff" clock, next to a locked
filing cabinet labeled "Acme internal docs."

**Talking points:** Claude was trained on public data up to a point in
time. It has never seen your company's service catalog, your internal wiki,
or any document that isn't public. That's not a bug — it's a starting
assumption we have to design around.

---

### Slide 2 — What Happens Without RAG?

**Live-demo cue:** Open the app's Chat tab. Ask *"What services does
Acme offer?"* and click **Ask Claude Directly**.

**Talking points:** Watch Claude either admit it doesn't know, or —more
interesting for the room— confidently guess a plausible-sounding number
that is not grounded in anything real. This is the problem RAG solves.

---

### Slide 3 — The RAG Idea

**Visual:** Question → Retrieve → Augment → Generate → Answer.

**Talking points:** Retrieval-Augmented Generation means retrieving
relevant external information *before* asking a language model to generate
an answer. Two separate steps, cleanly divided.

---

### Slide 4 — RAG in One Sentence

**Visual:** Large centered text.

> **Your code retrieves the knowledge. Claude generates the answer.**

**Talking points:** Say this sentence out loud. Everything in the rest of
the workshop is just detail underneath this one idea.

---

### Slide 5 — Documents → Embeddings

**Visual:** A sentence turning into a row of numbers.

**Talking points:** An embedding is a numerical vector that represents
semantic meaning. Two pieces of text that mean similar things end up with
similar vectors — even without sharing exact words. This runs locally and
is free.

---

### Slide 6 — Why Chunking Exists

**Live-demo cue:** Open **Experiments → Chunk Size**, re-index with chunk
size 150, then 1000, and show how the chunk count and retrieved results
change.

**Talking points:** We can't embed a whole document as one vector — that
would blend every idea in the document into one blurry average. Chunking
splits documents into smaller, focused, retrievable units.

---

### Slide 7 — Vector Search

**Visual:** A query vector with distance lines to nearby stored vectors.

**Talking points:** ChromaDB stores every chunk's vector locally and finds
the closest ones to a query vector. Chroma does NOT generate anything — it
is a search index over numbers.

---

### Slide 8 — Full RAG Architecture

**Visual:** The full pipeline diagram from the README.

**Talking points:** Walk through all 8 stages end to end: Documents →
Chunking → Embeddings → Vector Store → Query Embedding → Retrieval → Prompt
→ Claude → Answer.

---

### Slide 9 — Live Demo

**Live-demo cue:** Ask the same services question with **Run RAG**. Open the
Retrieval panel (show similarity scores), then the Prompt Inspector (show
the exact text sent to Claude).

**Talking points:** This is the "aha" moment — the room sees the actual
prompt, not a black box.

---

### Slide 10 — Break the RAG System

**Live-demo cue:** Ask *"What was Acme's revenue last year?"* in
**Experiments → Retrieval Failure**.

**Talking points:** When similarity falls below threshold, a properly
grounded system refuses to answer rather than fabricating one. Show the
warning message live.

---

### Slide 11 — RAG OFF vs RAG ON

**Live-demo cue:** Use the **Pipeline** tab's side-by-side comparison for
the services question.

**Talking points:** Same question, two paths. One makes no claim of
private knowledge; the other is grounded in a cited source document.

---

### Slide 12 — Where RAG Fails

**Talking points:** RAG doesn't eliminate hallucination — a model can still
ignore instructions or blend retrieved facts with unrelated training
knowledge. Poor chunking, a bad embedding model, or a too-low threshold can
all cause retrieval to miss the right answer. RAG raises the floor; it
doesn't guarantee correctness.

---

### Slide 13 — Production RAG

**Talking points:** This lab keeps everything local and simple for
teaching. A production system would add: access control per document,
re-ranking, hybrid keyword+vector search, evaluation pipelines, chunk
freshness/versioning, and monitoring for retrieval quality drift.

---

### Slide 14 — Three Takeaways

1. Retrieval and generation are separate steps — you can inspect, swap, or
   debug each one independently.
2. A similarity score is closeness, not confidence.
3. Grounding reduces hallucination but doesn't guarantee correctness — a
   well-designed system says "I don't know" instead of guessing.

---

## Suggested workshop demo sequence

Run these in order, live, using the app:

1. Ask Claude directly (no RAG) — services question.
2. Same question, with RAG.
3. Open retrieval results.
4. Open the exact prompt sent to Claude.
5. Change Top-K.
6. Change chunk size.
7. Ask a question with no matching information.
8. Turn RAG off again for contrast.
9. Use semantic search without Claude.
10. Walk through the Obsidian Canvas architecture diagram.

Reinforce throughout: **Retrieve ≠ Generate.**
