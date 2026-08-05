"""LLM Recommendation Orchestrator."""

from typing import Any, Dict

from llm_service.prompts import (
    ANALYST_RECOMMENDATION_SYSTEM_PROMPT,
    build_analyst_prompt,
)
from llm_service.providers.base import BaseLLMProvider
from llm_service.providers.groq_provider import GroqProvider
from llm_service.safety import sanitize_input_text


def get_threat_recommendation(
    user_id: str,
    risk_score: float,
    risk_level: str,
    shap_explanation: Dict[str, float],
    recent_activity: Dict[str, Any],
    provider: BaseLLMProvider = GroqProvider(),
) -> Dict[str, Any]:
    """Orchestrates prompt construction, sanitization, and provider invocation.

    Args:
        user_id: Target user identifier.
        risk_score: Risk score [0.0, 1.0].
        risk_level: Categorized risk bucket.
        shap_explanation: Top SHAP attributions dictionary.
        recent_activity: Activity counts dictionary.
        provider: Active BaseLLMProvider implementation instance.

    Returns:
        Structured recommendation dictionary.
    """
    clean_user_id = sanitize_input_text(user_id)
    prompt = build_analyst_prompt(
        user_id=clean_user_id,
        risk_score=risk_score,
        risk_level=risk_level,
        shap_explanation=shap_explanation,
        recent_activity=recent_activity,
    )
    return provider.generate_recommendation(
        prompt=prompt, system_prompt=ANALYST_RECOMMENDATION_SYSTEM_PROMPT
    )
