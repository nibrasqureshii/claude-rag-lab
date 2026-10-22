# Prompt Construction

This is the step where retrieved context becomes actual input text for
Claude. Nothing here is hidden behind a framework — the app's **Prompt
Inspector** shows you the *exact* string sent to the model.

## The shape of the prompt

```text
SYSTEM INSTRUCTIONS (sent separately, as the `system` parameter)
──────────────────────────────────────────────────────────────
You are answering questions using a private knowledge base.

Rules:
- Use only the provided context.
- Do not invent facts not supported by the context.
- If the answer is not present in the context, say:
  "I don't have enough information in the knowledge base."

USER MESSAGE
──────────────────────────────────────────────────────────────
CONTEXT

[Source: company.md | chunk: 0]
Acme provides technology services across five main areas: AI &
Automation, Data & Analytics, Platform Solutions...

[Source: products.md | chunk: 0]
Acme is a custom software development firm; it does not sell packaged
physical products...

QUESTION

What services does Acme offer?
```

## Why label each chunk with its source?

So that when Claude's answer references a fact, a human reader (or Claude
itself, if asked to cite) can trace that fact back to a specific document
and chunk. This is what powers the app's **Sources** display and the
**Explain This Answer** feature — both are built directly from this
labeled context, not from a second question asked to Claude.

## Why does the system prompt explicitly say "don't invent facts"?

Because a language model, left to its own devices, will happily generate a
fluent, confident-sounding answer even when it has no real basis for one.
Explicitly instructing the model to admit uncertainty is one of the
cheapest and most effective defenses against this. See [[hallucination]].
