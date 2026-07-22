"""Ollama local provider implementation.

Calls a locally-running Ollama instance for fully offline/on-prem
LLM inference. Ideal for development and data-sovereign deployments.
"""

from base import BaseProvider


class OllamaProvider(BaseProvider):
    """LLM provider backed by a local Ollama instance."""

    def __init__(
        self, host: str = "http://localhost:11434", model: str = "llama3.1:8b"
    ) -> None:
        """Initialise with Ollama host and model.

        Args:
            host: Base URL of the Ollama server.
            model: Model tag available in the local Ollama instance.

        """
        self._host = host.rstrip("/")
        self._model = model

    def complete(self, prompt: str, **kwargs) -> str:
        """Call Ollama generate endpoint.

        Args:
            prompt: Full prompt string.
            **kwargs: temperature, max_tokens, etc.

        Returns:
            The model's response text.

        Todo:
            Implement actual HTTP call in Week 7.

        """
        raise NotImplementedError("Week 7 — implement Ollama API call.")
