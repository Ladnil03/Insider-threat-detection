"""Provider Factory for Dynamic LLM Backend Instantiation."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from llm_service.providers.base import BaseLLMProvider
from llm_service.providers.groq_provider import GroqProvider
from llm_service.providers.ollama_provider import OllamaProvider

CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"


def load_llm_config() -> Dict[str, Any]:
    """Loads LLM service YAML configuration."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def get_llm_provider(
    provider_name: Optional[str] = None,
    model_name: Optional[str] = None,
) -> BaseLLMProvider:
    """Factory creating the configured BaseLLMProvider instance.

    Args:
        provider_name: Explicit provider name ('groq' or 'ollama'). Defaults to LLM_PROVIDER env var or config.
        model_name: Optional override for model name.

    Returns:
        Instantiated BaseLLMProvider.
    """
    config = load_llm_config()
    active = (
        provider_name
        or os.getenv("LLM_PROVIDER")
        or config.get("active_provider", "groq")
    ).lower()

    if active == "ollama":
        ollama_cfg = config.get("providers", {}).get("ollama", {})
        model = (
            model_name or os.getenv("LLM_MODEL") or ollama_cfg.get("model", "llama3:8b")
        )
        base_url = os.getenv("OLLAMA_BASE_URL") or ollama_cfg.get(
            "base_url", "http://localhost:11434"
        )
        timeout = float(ollama_cfg.get("timeout_seconds", 30))
        return OllamaProvider(model=model, base_url=base_url, timeout_seconds=timeout)

    # Default to Groq provider
    groq_cfg = config.get("providers", {}).get("groq", {})
    model = (
        model_name
        or os.getenv("LLM_MODEL")
        or groq_cfg.get("default_model", "llama-3.3-70b-versatile")
    )
    timeout = float(groq_cfg.get("timeout_seconds", 20))
    max_retries = int(groq_cfg.get("max_retries", 3))

    return GroqProvider(model=model, timeout_seconds=timeout, max_retries=max_retries)
