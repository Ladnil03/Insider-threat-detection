"""Abstract provider interface for LLM inference.

All providers (Groq, Ollama, future) must implement this interface
so the orchestration layer never depends on a specific provider.
"""

from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def complete(self, prompt: str, **kwargs) -> str:
        """Send a prompt to the LLM and return the completion.

        Args:
            prompt: The full prompt string.
            **kwargs: Provider-specific parameters (temperature, max_tokens, etc.).

        Returns:
            The model's text completion.

        """
        ...
