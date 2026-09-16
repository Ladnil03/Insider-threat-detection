"""Ollama Local / On-Prem Provider Implementation."""

import json
import logging
from typing import Any, Dict

import httpx

from llm_service.providers.base import BaseLLMProvider

logger = logging.getLogger(__name__)


class OllamaProvider(BaseLLMProvider):
    """Local Ollama provider preserving complete on-prem data sovereignty."""

    def __init__(
        self,
        model: str = "llama3:8b",
        base_url: str = "http://localhost:11434",
        timeout_seconds: float = 30.0,
    ) -> None:
        """Initializes Ollama provider settings.

        Args:
            model: Ollama model tag (default: llama3:8b).
            base_url: Ollama server HTTP endpoint URL.
            timeout_seconds: HTTP request timeout.
        """
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def generate_recommendation(
        self,
        prompt: str,
        system_prompt: str,
        json_mode: bool = True,
        temperature: float = 0.1,
    ) -> Dict[str, Any]:
        """Queries local Ollama instance with optional JSON format.

        Args:
            prompt: Formatted user risk summary prompt.
            system_prompt: Persona system prompt.
            json_mode: Whether to enforce JSON mode.
            temperature: Sampling temperature.

        Returns:
            Dictionary containing 'text', 'model', 'provider', and 'status'.
        """
        payload: Dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {"temperature": temperature},
        }
        if json_mode:
            payload["format"] = "json"

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                resp = client.post(f"{self.base_url}/api/generate", json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    return {
                        "text": data.get("response", "").strip(),
                        "model": self.model,
                        "provider": "ollama",
                        "status": "success",
                    }
                else:
                    return {
                        "text": f"Error: Ollama returned status {resp.status_code}: {resp.text}",
                        "model": self.model,
                        "provider": "ollama",
                        "status": "error",
                    }
        except httpx.ConnectError:
            logger.info(
                "Ollama server not reachable at %s. Returning local stub.",
                self.base_url,
            )
            mock_payload = {
                "summary": "[Ollama Offline] User exhibits behavioral deviations requiring analyst triage.",
                "risk_drivers": [
                    {
                        "feature": "Logon Activity",
                        "impact": "MEDIUM",
                        "description": "Off-hours authentication detected.",
                    }
                ],
                "recommended_action": "Verify credentials and prompt user MFA.",
                "urgency": "MEDIUM",
            }
            return {
                "text": json.dumps(mock_payload),
                "model": self.model,
                "provider": "ollama",
                "status": "mock",
            }
        except Exception as e:
            return {
                "text": f"Error: Failed to communicate with Ollama: {str(e)}",
                "model": self.model,
                "provider": "ollama",
                "status": "error",
            }
