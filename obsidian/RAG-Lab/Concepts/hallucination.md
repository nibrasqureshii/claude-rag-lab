# Hallucination

A "hallucination" is when a language model produces a fluent, confident
statement that is not actually supported by any real source — it sounds
right, but nobody ever told the model this fact, and it isn't true (or
isn't verifiable).

## Why does this happen?

A model like Claude is trained to produce plausible, well-formed text. When
asked a specific factual question it doesn't actually know the answer to
(for example, private information about a company like Acme that isn't
in its training data), it can still generate *something* that reads exactly
like a correct answer, because "sounding correct" and "being correct" are
not the same skill.

## How grounding helps

RAG reduces hallucination by giving the model real source text and
explicitly instructing it to answer *only* from that text — see
[[prompt-construction]]. If the retrieved context doesn't contain the
answer, a well-designed system should say so plainly:

```text
"I don't have enough information in the knowledge base."
```

rather than inventing a plausible-sounding fabrication.

## This does not make hallucination impossible

Grounding reduces the *risk* of hallucination, but does not eliminate it —
a model can still, in principle, ignore its instructions or blend retrieved
facts with unrelated training knowledge. That's why the app never claims a
[[vector-search|similarity score]] is a guarantee of correctness, and why
the **Retrieval Failure** experiment deliberately shows the system refusing
to answer when nothing relevant was found, rather than silently trusting
the model.

## Try it yourself

In the app, ask a question with RAG turned **off** — for example, "What
services does Acme offer?" Claude may confidently guess a
plausible-sounding answer. Then run the same question with RAG **on** and
compare. See [[RAG]].
