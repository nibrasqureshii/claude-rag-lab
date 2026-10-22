"""
Stage 7 of the RAG pipeline: the CLAUDE CLIENT.

This is a thin wrapper around the official `anthropic` Python SDK. Its only
job is: send a prompt (plus optional system instructions) to Claude, and
return the answer text along with a little bit of metadata useful for
teaching (model name, token usage, timing).

This is intentionally NOT a generic AI framework. There is no chain, no
agent loop, no tool use here — just one Messages API call.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass

import anthropic

DEFAULT_MAX_TOKENS = 1024


class ClaudeConfigError(RuntimeError):
    """Raised when required Claude configuration (API key/model) is missing."""


class ClaudeAPIError(RuntimeError):
    """Raised when the Anthropic API call itself fails."""


@dataclass
class ClaudeResponse:
    """The result of one Claude call, plus teaching-friendly metadata."""

    text: str
    model: str
    input_tokens: int | None
    output_tokens: int | None
    elapsed_seconds: float


def _get_api_key() -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        raise ClaudeConfigError(
            "Anthropic API key is missing. Add ANTHROPIC_API_KEY to your .env file."
        )
    return api_key


def _get_model() -> str:
    model = os.environ.get("ANTHROPIC_MODEL", "").strip()
    if not model:
        raise ClaudeConfigError(
            "No Claude model configured. Add ANTHROPIC_MODEL to your .env file."
        )
    return model


class ClaudeClient:
    """Thin wrapper around anthropic.Anthropic for one-shot Q&A calls."""

    def __init__(self):
        self.api_key = _get_api_key()
        self.model = _get_model()
        # The SDK reads the key we pass explicitly; we never log or print it.
        self._client = anthropic.Anthropic(api_key=self.api_key)

    def answer_question(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
    ) -> ClaudeResponse:
        """Send one prompt to Claude and return the answer plus metadata."""
        start = time.perf_counter()
        try:
            kwargs = {
                "model": self.model,
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}],
            }
            if system_prompt:
                kwargs["system"] = system_prompt

            message = self._client.messages.create(**kwargs)
        except anthropic.APIStatusError as exc:
            raise ClaudeAPIError(
                "Claude API request failed.\n\nCheck:\n"
                "1. API key\n2. model name\n3. network connection\n"
                "4. available API credits\n\n"
                f"(technical detail: HTTP {exc.status_code})"
            ) from exc
        except anthropic.APIConnectionError as exc:
            raise ClaudeAPIError(
                "Claude API request failed: could not reach the Anthropic API.\n"
                "Check your network connection."
            ) from exc

        elapsed = time.perf_counter() - start

        text = "".join(block.text for block in message.content if block.type == "text")
        usage = getattr(message, "usage", None)

        return ClaudeResponse(
            text=text,
            model=message.model,
            input_tokens=getattr(usage, "input_tokens", None),
            output_tokens=getattr(usage, "output_tokens", None),
            elapsed_seconds=elapsed,
        )


_cached_client: ClaudeClient | None = None


def get_claude_client() -> ClaudeClient:
    """Return a process-wide singleton ClaudeClient (mirrors get_embedder)."""
    global _cached_client
    if _cached_client is None:
        _cached_client = ClaudeClient()
    return _cached_client
