"""Groq Cloud API Provider Implementation using the official Groq Python SDK."""

import json
import logging
import os
import time
from typing import Any, Dict, Optional

from groq import APIConnectionError, APIError, Groq, RateLimitError

from llm_service.providers.base import BaseLLMProvider

logger = logging.getLogger(__name__)


class GroqProvider(BaseLLMProvider):
    """Groq API provider for open-weight high-speed LLM inference."""

    def __init__(
        self,
        model: str = "llama-3.3-70b-versatile",
        api_key: Optional[str] = None,
        max_retries: int = 3,
        timeout_seconds: float = 20.0,
    ) -> None:
        """Initializes Groq provider settings.

        Args:
            model: Target open-weight model deployed on Groq (default: llama-3.3-70b-versatile).
            api_key: Groq API key (defaults to GROQ_API_KEY env var).
            max_retries: Maximum exponential backoff retries on rate limits.
            timeout_seconds: Client request timeout limit.
        """
        self.model = model
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "").strip()
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds

        self._client: Optional[Groq] = None
        if self.api_key:
            self._client = Groq(api_key=self.api_key, timeout=self.timeout_seconds)

    def generate_recommendation(
        self,
        prompt: str,
        system_prompt: str,
        json_mode: bool = True,
        temperature: float = 0.1,
    ) -> Dict[str, Any]:
        """Queries Groq API endpoint for analyst threat recommendation with rate-limit retries.

        Args:
            prompt: Formatted user risk summary prompt.
            system_prompt: Persona system prompt.
            json_mode: Whether to enforce native JSON object output format.
            temperature: Sampling temperature.

        Returns:
            Dictionary containing 'text', 'model', 'provider', and 'status'.
        """
        if not self.api_key or not self._client:
            logger.info(
                "GROQ_API_KEY not configured. Returning deterministic mock response."
            )
            mock_payload = {
                "summary": "User activity exhibits abnormal behavioral departure from established benign baseline.",
                "risk_drivers": [
                    {
                        "feature": "USB File Transfers",
                        "impact": "HIGH",
                        "description": "Acute volume spike in removable media transfers.",
                    }
                ],
                "recommended_action": "Initiate tier-1 SOC host audit and review USB authorization.",
                "urgency": "HIGH",
            }
            return {
                "text": json.dumps(mock_payload),
                "model": self.model,
                "provider": "groq",
                "status": "mock",
            }

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        kwargs: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        attempt = 0
        backoff = 1.0

        while attempt < self.max_retries:
            attempt += 1
            try:
                chat_completion = self._client.chat.completions.create(**kwargs)
                response_text = chat_completion.choices[0].message.content or ""
                usage = getattr(chat_completion, "usage", None)

                return {
                    "text": response_text.strip(),
                    "model": self.model,
                    "provider": "groq",
                    "status": "success",
                    "usage": (
                        {
                            "prompt_tokens": usage.prompt_tokens,
                            "completion_tokens": usage.completion_tokens,
                            "total_tokens": usage.total_tokens,
                        }
                        if usage
                        else {}
                    ),
                }

            except RateLimitError as e:
                logger.warning(
                    f"Groq RateLimitError on attempt {attempt}/{self.max_retries}: {e}. Backing off for {backoff:.1f}s."
                )
                if attempt >= self.max_retries:
                    return {
                        "text": f"Error: Groq rate limit exceeded after {self.max_retries} retries: {str(e)}",
                        "model": self.model,
                        "provider": "groq",
                        "status": "rate_limited",
                    }
                time.sleep(backoff)
                backoff *= 2.0

            except APIConnectionError as e:
                logger.warning(f"Groq connection error on attempt {attempt}: {e}")
                if attempt >= self.max_retries:
                    return {
                        "text": f"Error: Groq connection failed: {str(e)}",
                        "model": self.model,
                        "provider": "groq",
                        "status": "connection_error",
                    }
                time.sleep(backoff)
                backoff *= 1.5

            except APIError as e:
                logger.error(f"Groq APIError: {e}")
                return {
                    "text": f"Error: Groq API call failed: {str(e)}",
                    "model": self.model,
                    "provider": "groq",
                    "status": "api_error",
                }

            except Exception as e:
                logger.error(f"Unexpected error in Groq provider: {e}")
                return {
                    "text": f"Error: Unexpected LLM error: {str(e)}",
                    "model": self.model,
                    "provider": "groq",
                    "status": "error",
                }

        return {
            "text": "Error: Maximum LLM provider retry attempts exhausted.",
            "model": self.model,
            "provider": "groq",
            "status": "failed",
        }
