"""Groq API provider implementation.

Uses httpx to call the Groq REST API (free tier) with open-weight
models like llama-3.1-8b-instant or deepseek-r1-distill-llama-70b.
"""

from base import BaseProvider


class GroqProvider(BaseProvider):
    """LLM provider backed by the Groq free-tier API."""

    def __init__(self, api_key: str, model: str = "llama-3.1-8b-instant") -> None:
        """Initialise with API key and model name.

        Args:
            api_key: Groq API key.
            model: Model identifier supported by Groq.

        """
        self._api_key = api_key
        self._model = model

    def complete(self, prompt: str, **kwargs) -> str:
        """Call Groq chat completions endpoint.

        Args:
            prompt: Full prompt string.
            **kwargs: temperature, max_tokens, etc.

        Returns:
            The model's response text.

        Todo:
            Implement actual HTTP call in Week 7.

        """
        raise NotImplementedError("Week 7 — implement Groq API call.")
