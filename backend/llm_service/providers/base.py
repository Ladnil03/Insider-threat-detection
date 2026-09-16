"""Abstract Interface for LLM Service Providers."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseLLMProvider(ABC):
    """Abstract base class establishing uniform interface for all LLM providers."""

    @abstractmethod
    def generate_recommendation(
        self,
        prompt: str,
        system_prompt: str,
        json_mode: bool = True,
        temperature: float = 0.1,
    ) -> Dict[str, Any]:
        """Generates plain-English analyst recommendation from prompt.

        Args:
            prompt: User-specific threat context prompt.
            system_prompt: System prompt instructing LLM persona and format.
            json_mode: If True, instructs provider to enforce structured JSON output.
            temperature: Sampling temperature for deterministic generation.

        Returns:
            Dictionary containing raw output string/json, model name, and provider status.
        """
        pass
