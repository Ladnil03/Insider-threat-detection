"""Ollama Local / On-Prem Provider Implementation."""

from typing import Any, Dict

from llm_service.providers.base import BaseLLMProvider


class OllamaProvider(BaseLLMProvider):
    """Local Ollama provider preserving complete on-prem data sovereignty."""

    def __init__(
        self, model: str = "llama3:8b", base_url: str = "http://localhost:11434"
    ) -> None:
        """Initializes Ollama provider settings.

        Args:
            model: Ollama model tag.
            base_url: Ollama server HTTP endpoint.
        """
        self.model = model
        self.base_url = base_url

    def generate_recommendation(
        self, prompt: str, system_prompt: str
    ) -> Dict[str, Any]:
        """Queries local Ollama instance.

        Args:
            prompt: Formatted user risk summary prompt.
            system_prompt: Persona system prompt.

        Returns:
            Dictionary with response text, model name, and status.
        """
        return {
            "text": "[Ollama Local Stub] Recommended Action: Conduct secondary host audit.",
            "model": self.model,
            "provider": "ollama",
            "status": "mock",
        }
