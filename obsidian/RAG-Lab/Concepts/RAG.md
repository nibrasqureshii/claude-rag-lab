# RAG (Retrieval-Augmented Generation)

Retrieval-Augmented Generation means **retrieving relevant external
information before asking a language model to generate an answer.**

Without RAG, a model like Claude can only answer using what it learned
during training. It has never seen your private documents, your internal
wiki, or Acme's service catalog.

With RAG, your own code searches a private knowledge base *first*, hands
the most relevant pieces to Claude as context, and only then asks Claude to
answer. Claude never "reaches into" a database on its own — your code does
that step, then simply pastes the result into the prompt.

## The diagram

```text
Question
   │
   ▼
Retrieve relevant chunks (your code + vector database)
   │
   ▼
Build a prompt containing those chunks + the question
   │
   ▼
Claude generates an answer using ONLY that prompt
```

## The one sentence that matters

> **Your code retrieves the knowledge. Claude generates the answer.**

Retrieval and generation are two separate, swappable steps. See
[[vector-search]] and [[retrieval]] for how the first step works, and
[[prompt-construction]] for how the two steps are stitched together.
