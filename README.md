# Claude RAG Lab

**See exactly how Retrieval-Augmented Generation works.**

This is an educational, fully observable RAG (Retrieval-Augmented
Generation) laboratory built in Python. It is designed for a workshop
audience of junior developers who have never built a RAG system before, and
it deliberately avoids hiding any mechanics behind a framework.

> **Your code retrieves the knowledge. Claude generates the answer.**

That sentence is the whole point of this project. Everything else — the
UI, the experiments, the Obsidian vault — exists to make that sentence feel
concrete instead of abstract.

---

## 1. What is RAG?

A language model like Claude is very good at generating fluent, well
reasoned text, but it only knows what it learned during training. It has
never seen your company's internal refund policy, your product catalog, or
any other private document.

**Retrieval-Augmented Generation** fixes this by adding a step *before*
generation: your own code searches a private knowledge base for the most
relevant pieces of text, and hands those pieces to Claude as context inside
the prompt. Claude then generates an answer using only what it was given.

```text
Question
   │
   ▼
Your code searches a private knowledge base (retrieval)
   │
   ▼
The most relevant text becomes part of the prompt (augmentation)
   │
   ▼
Claude generates an answer from that prompt (generation)
```

Claude never queries the database itself. Your code does that, then simply
pastes the results into a normal text prompt.

## 2. What this demo teaches

- What an embedding is, and why text becomes a vector of numbers.
- Why documents are split into chunks before being searched.
- How a vector database (Chroma) finds semantically similar chunks.
- What "Top-K" and "similarity threshold" mean and how to tune them.
- How retrieved chunks are assembled into the exact prompt sent to Claude.
- Why RAG reduces (but does not eliminate) hallucination.
- That retrieval and generation are two separate, swappable steps.

By the end, you should be able to answer every question in the
[Success Criteria](#12-success-criteria) section below.

## 3. Architecture

```text
┌────────────┐   ┌──────────┐   ┌────────────┐   ┌──────────────┐
│ Documents  │──▶│ Chunking │──▶│ Embeddings │──▶│ Chroma        │
│ (Markdown) │   │          │   │ (local)    │   │ Vector Store  │
└────────────┘   └──────────┘   └────────────┘   └──────┬───────┘
                                                          │
                          ┌───────────────────────────────┘
                          ▼
                 ┌──────────────────┐   ┌──────────────┐   ┌─────────┐
Question  ──────▶│ Query Embedding  │──▶│ Similarity    │──▶│ Top-K   │
                 └──────────────────┘   │ Retrieval     │   │ Context │
                                        └──────────────┘   └────┬────┘
                                                                 ▼
                                                         ┌───────────────┐
                                                         │ Prompt Builder │
                                                         └───────┬───────┘
                                                                 ▼
                                                         ┌───────────────┐
                                                         │ Claude API     │
                                                         └───────┬───────┘
                                                                 ▼
                                                       Answer + Sources
```

Code lives in small, single-responsibility modules under `app/rag/`, one
per pipeline stage:

```text
app/rag/
├── loader.py           Stage 1 — load Markdown files into Documents
├── chunker.py           Stage 2 — split Documents into overlapping Chunks
├── embedder.py           Stage 3 — turn text into vectors (local model)
├── vector_store.py        Stage 4 — Chroma wrapper (store + search vectors)
├── retriever.py            Stage 5 — question -> query embedding -> Top-K
├── prompt_builder.py        Stage 6 — assemble the exact Claude prompt
├── claude_client.py           Stage 7 — thin wrapper around the Anthropic SDK
└── pipeline.py                    glue: runs all stages, records timings
```

No LangChain, no LlamaIndex — every step above is plain, readable Python
that a junior developer can open and understand end to end.

## 4. Installation

Requires **Python 3.11+** (this project was developed against 3.12).

```bash
cd claude-rag-lab
python3 -m venv .venv
source .venv/bin/activate        # on Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

The first run will download the local embedding model
(`sentence-transformers/all-MiniLM-L6-v2`, ~90MB) and cache it — this can
take a minute the very first time.

## 5. Environment variables

Create a `.env` file in the project root (copy `.env.example` if present,
or create it fresh):

```env
ANTHROPIC_API_KEY=your-key-here
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929
```

- `ANTHROPIC_API_KEY` is the **only** paid dependency in this entire
  project. Everything else (embeddings, vector search) runs locally for
  free.
- Never commit a real API key. `.env` is already listed in `.gitignore`.
- If the key is missing, the app will show a clear, friendly error instead
  of a raw traceback — it will never print the key itself.

## 6. Running the app

```bash
streamlit run app/main.py
```

On first launch, go to the **Knowledge Base** tab and click **Re-index**
to build the vector database from the sample documents in `knowledge/`.

## 7. How ingestion works

1. `loader.py` recursively reads every `.md` file under `knowledge/` into a
   `Document` (text + metadata: source filename, path, first heading).
2. `chunker.py` splits each document's text into overlapping word-based
   chunks (default: 500 words, 75-word overlap), tagging each chunk with
   its source, section, and a stable ID like `refund-policy::chunk-003`.
3. `embedder.py` turns every chunk's text into a 384-dimensional vector
   using a local `sentence-transformers` model — no API call, no cost.
4. `vector_store.py` stores each chunk's vector, text, and metadata in a
   local, persistent Chroma collection at `data/chroma/`.

## 8. How retrieval works

1. The user's question is embedded with the *same* local model used for
   the documents (`embedder.embed_query`).
2. `vector_store.py` asks Chroma for the closest stored vectors.
3. `retriever.py` converts Chroma's raw distance numbers into an intuitive
   0–1 "similarity" score, keeps only the top **K** results, and optionally
   drops anything below a configured similarity **threshold**.

The similarity score is a closeness measure, not a probability — the app
says this explicitly in the Retrieval panel.

## 9. How Claude receives context

`prompt_builder.py` assembles the retrieved chunks and the user's question
into one exact string, labeled by source and chunk index, together with
system instructions that tell Claude to answer only from the provided
context and to admit when it doesn't know. The **Prompt Inspector** in the
app shows you this exact string — nothing is hidden.

`claude_client.py` is a thin wrapper around the official `anthropic` SDK
that sends this prompt via the Messages API and returns the answer text
plus basic metadata (model name, token usage, timing).

## 10. How to use the experiments

Open the **Experiments** tab in the app:

- **Top-K** — slide K from 1 to 10 and see how retrieved results and total
  context size change for the same question.
- **Chunk Size** — change chunk size/overlap, re-index, and watch the
  chunk count and retrieval results shift.
- **Retrieval Failure** — ask something the knowledge base has no answer
  for (e.g. *"What was Acme's revenue last year?"*) and watch the system
  refuse to fabricate an answer once similarity falls below the threshold.
- **Remove Context** — deselect retrieved chunks before asking Claude,
  proving that retrieval and generation are separate steps.
- **Semantic Search** — search the knowledge base without ever calling
  Claude, to isolate what retrieval alone actually does.

Standalone equivalents of some of these live in `experiments/*.py` and can
be run directly from the terminal (see each script's docstring).

## 11. How to open the Obsidian vault

The `obsidian/RAG-Lab/` folder is a self-contained
[Obsidian](https://obsidian.md) vault used purely for human-friendly
knowledge authoring, concept notes, and architecture visualization. **It is
not required to run the app** — Chroma remains the actual vector database.

To open it: install Obsidian, choose "Open folder as vault," and select
`obsidian/RAG-Lab/`. Start with `Architecture/00 - How RAG Works.canvas`
for a visual walkthrough, then explore `Concepts/` for junior-friendly
explanations of each idea (`RAG.md`, `embeddings.md`, `chunking.md`,
`vector-search.md`, `retrieval.md`, `prompt-construction.md`,
`hallucination.md`).

## 12. Success criteria

A junior developer who has gone through this lab should be able to answer:

- **What is an embedding?** A numerical representation of text that can be
  compared for semantic similarity.
- **What is a chunk?** A smaller portion of a source document used as a
  retrievable unit.
- **What is a vector database?** A system that stores vectors and
  efficiently searches for similar vectors.
- **What does retrieval do?** Finds relevant knowledge.
- **What does Claude do?** Generates a response using the supplied context.
- **Does Chroma generate the answer?** No.
- **Does Claude search Chroma automatically?** No.
- **Why is chunking important?** Because retrieval operates on the chunks
  we choose to create.
- **Why can more chunks be worse?** Because irrelevant context can dilute
  useful context.
- **What happens when the knowledge base doesn't contain the answer?** A
  properly grounded system says it does not have enough information,
  rather than inventing an answer.

## 13. Running tests

```bash
pytest
```

Unit tests cover the loader, chunker, retriever (with a mocked vector
store/embedder), and prompt builder. They do **not** require an Anthropic
API key or a downloaded embedding model. Optional integration scripts that
do call the real Claude API live in `experiments/`.

## 14. Project layout

```text
claude-rag-lab/
├── app/
│   ├── main.py            Streamlit entrypoint
│   ├── resources.py        Cached embedder/vector-store/Claude client
│   ├── styles.py             Shared CSS
│   ├── rag/                    Core pipeline modules (see Architecture)
│   └── ui/                       Chat, Retrieval, Pipeline, Experiments views
├── knowledge/               Sample documents for a fictional company (Acme Software Co.)
├── data/chroma/               Local persistent Chroma database (gitignored)
├── obsidian/RAG-Lab/            Obsidian vault: concepts + architecture canvas
├── experiments/                    Standalone terminal scripts
├── tests/                            Pytest unit tests
├── presentation/                       Workshop slide outline
├── .env.example
└── pyproject.toml
```

## 15. Important constraints (by design)

- No hosted vector database — Chroma runs locally against `data/chroma/`.
- No paid embedding API — embeddings run locally via `sentence-transformers`.
- No LangChain or LlamaIndex — every pipeline stage is plain Python.
- Obsidian is optional and never a runtime dependency of the app.
- The only required external service is the Anthropic Claude API.
