"""
Glue layer that runs the full RAG pipeline end-to-end and records exactly
what happened at each stage, with timings. This is what the UI renders --
one `PipelineRun` object holds everything needed by the Chat tab, the
Retrieval panel, the Prompt Inspector, the Pipeline Visualization, and the
"Explain This Answer" feature, so every view is guaranteed to describe the
same run instead of six views quietly re-deriving slightly different data.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from app.rag.claude_client import ClaudeClient, ClaudeResponse
from app.rag.embedder import Embedder
from app.rag.prompt_builder import SYSTEM_PROMPT, build_prompt
from app.rag.retriever import RetrievalResult, retrieve
from app.rag.vector_store import VectorStore


@dataclass
class PipelineTimings:
    embedding_ms: float = 0.0
    retrieval_ms: float = 0.0
    prompt_ms: float = 0.0
    claude_ms: float = 0.0

    @property
    def total_ms(self) -> float:
        return self.embedding_ms + self.retrieval_ms + self.prompt_ms + self.claude_ms


@dataclass
class PipelineRun:
    """Full record of one RAG question, one stage at a time."""

    question: str
    rag_enabled: bool
    retrieved: list[RetrievalResult] = field(default_factory=list)
    included_chunk_ids: set[str] = field(default_factory=set)
    prompt: str | None = None
    system_prompt: str | None = None
    answer: ClaudeResponse | None = None
    timings: PipelineTimings = field(default_factory=PipelineTimings)
    query_vector_preview: list[float] = field(default_factory=list)
    below_threshold: bool = False
    best_score: float | None = None
    threshold: float | None = None
    error: str | None = None

    @property
    def included_results(self) -> list[RetrievalResult]:
        """Chunks that were both retrieved AND left checked in the UI
        (see Experiment D: Remove Context)."""
        if not self.included_chunk_ids:
            return self.retrieved
        return [r for r in self.retrieved if r.chunk_id in self.included_chunk_ids]


def run_rag_pipeline(
    question: str,
    vector_store: VectorStore,
    embedder: Embedder,
    claude_client: ClaudeClient,
    top_k: int = 5,
    similarity_threshold: float | None = None,
    max_tokens: int = 1024,
) -> PipelineRun:
    """Run the full RAG pipeline: embed -> retrieve -> build prompt -> ask Claude."""
    run = PipelineRun(question=question, rag_enabled=True)

    t0 = time.perf_counter()
    query_vector = embedder.embed_query(question)
    run.timings.embedding_ms = (time.perf_counter() - t0) * 1000
    run.query_vector_preview = query_vector[:8]

    t0 = time.perf_counter()
    results = retrieve(question, vector_store, embedder, top_k=top_k, similarity_threshold=None)
    run.timings.retrieval_ms = (time.perf_counter() - t0) * 1000

    run.retrieved = results
    run.included_chunk_ids = {r.chunk_id for r in results}
    run.threshold = similarity_threshold
    run.best_score = max((r.score for r in results), default=0.0)

    if similarity_threshold is not None and run.best_score < similarity_threshold:
        run.below_threshold = True
        return run

    t0 = time.perf_counter()
    run.system_prompt = SYSTEM_PROMPT
    run.prompt = build_prompt(question, run.included_results)
    run.timings.prompt_ms = (time.perf_counter() - t0) * 1000

    try:
        run.answer = claude_client.answer_question(
            run.prompt, system_prompt=run.system_prompt, max_tokens=max_tokens
        )
        run.timings.claude_ms = run.answer.elapsed_seconds * 1000
    except Exception as exc:  # noqa: BLE001 - surfaced to the UI, not swallowed
        run.error = str(exc)

    return run


def run_direct_pipeline(
    question: str,
    claude_client: ClaudeClient,
    max_tokens: int = 1024,
) -> PipelineRun:
    """Ask Claude the question directly, with NO retrieval step at all.
    This is the "RAG OFF" comparison mode."""
    run = PipelineRun(question=question, rag_enabled=False)

    no_rag_system_prompt = (
        "Answer the user's question using only your general knowledge. "
        "You do not have access to any private or company-specific knowledge base."
    )
    run.system_prompt = no_rag_system_prompt
    run.prompt = question

    try:
        run.answer = claude_client.answer_question(
            question, system_prompt=no_rag_system_prompt, max_tokens=max_tokens
        )
        run.timings.claude_ms = run.answer.elapsed_seconds * 1000
    except Exception as exc:  # noqa: BLE001
        run.error = str(exc)

    return run
