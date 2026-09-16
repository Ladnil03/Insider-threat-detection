"""LLM Recommendation Orchestrator for SOC Analyst Threat Summaries."""

import json
import logging
import re
from typing import Any, Dict, List, Optional, Union

from llm_service.prompts import (
    ANALYST_RECOMMENDATION_SYSTEM_PROMPT,
    build_analyst_prompt,
)
from llm_service.providers.base import BaseLLMProvider
from llm_service.providers.factory import get_llm_provider
from llm_service.safety import sanitize_activity_metadata, sanitize_input_text

logger = logging.getLogger(__name__)


def _extract_json_object(raw_text: str) -> Optional[Dict[str, Any]]:
    """Extracts and parses JSON object from model output text, stripping extraneous markdown fences."""
    if not raw_text or not isinstance(raw_text, str):
        return None

    cleaned = raw_text.strip()
    # Strip markdown code blocks if model returned ```json ... ```
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()

    # Try direct parse
    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    # Regex search for outermost JSON object { ... }
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group(0))
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass

    return None


def get_threat_recommendation(
    user_id: str,
    risk_score: float,
    risk_level: str,
    prism_score: Optional[float] = None,
    sai_score: Optional[float] = None,
    shap_explanation: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
    recent_activity: Optional[Dict[str, Any]] = None,
    user_role: Optional[str] = None,
    policy_violations: Optional[List[Dict[str, Any]]] = None,
    provider: Optional[BaseLLMProvider] = None,
) -> Dict[str, Any]:
    """Orchestrates prompt construction, provider query, and structured JSON parsing.

    Args:
        user_id: Target user ID.
        risk_score: Composite / ensemble risk score [0.0, 1.0].
        risk_level: Categorized risk bucket (e.g. LOW, MODERATE, HIGH, CRITICAL).
        prism_score: Optional rule-based PRISM score.
        sai_score: Optional autoencoder reconstruction anomaly score.
        shap_explanation: SHAP feature attributions dictionary or list.
        recent_activity: Observed activity counts dictionary.
        user_role: Optional corporate role / privilege tier.
        policy_violations: Optional list of triggered policy rule events.
        provider: Optional BaseLLMProvider instance (defaults to factory provider).

    Returns:
        Structured recommendation dictionary containing:
        - summary: Plain-English incident narrative
        - risk_drivers: List of key behavioral risk drivers
        - recommended_action: Actionable mitigation advice
        - urgency: LOW | MEDIUM | HIGH | CRITICAL
        - raw_response: Original provider output
        - provider: Name of the LLM provider
        - model: LLM model tag
        - status: success | mock | fallback_raw_text | rate_limited | error
    """
    # 1. Sanitize all user-controlled inputs
    clean_user_id = sanitize_input_text(user_id, max_length=64)
    clean_role = sanitize_input_text(user_role, max_length=100) if user_role else None
    clean_activity = sanitize_activity_metadata(recent_activity or {})

    # 2. Build structured prompt
    prompt = build_analyst_prompt(
        user_id=clean_user_id,
        risk_score=risk_score,
        risk_level=risk_level,
        prism_score=prism_score,
        sai_score=sai_score,
        shap_explanation=shap_explanation,
        recent_activity=clean_activity,
        user_role=clean_role,
        policy_violations=policy_violations,
    )

    # 3. Resolve active LLM provider
    active_provider = provider if provider is not None else get_llm_provider()

    # 4. Invoke LLM provider
    resp = active_provider.generate_recommendation(
        prompt=prompt,
        system_prompt=ANALYST_RECOMMENDATION_SYSTEM_PROMPT,
        json_mode=True,
    )

    raw_text = resp.get("text", "")
    provider_name = resp.get("provider", "unknown")
    model_name = resp.get("model", "unknown")
    status = resp.get("status", "success")

    # 5. Handle rate limits and connection errors gracefully
    if status in ("rate_limited", "connection_error", "api_error", "failed"):
        logger.warning(f"LLM Provider error [{status}]: {raw_text}")
        return {
            "summary": f"Automated risk analysis: User exhibits {risk_level} risk score ({risk_score:.2f}). (LLM service temporarily unavailable: {status}).",
            "risk_drivers": [],
            "recommended_action": "Conduct standard SOC triage based on SHAP feature attributions and policy violation flags.",
            "urgency": (
                risk_level
                if risk_level in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
                else "HIGH"
            ),
            "raw_response": raw_text,
            "provider": provider_name,
            "model": model_name,
            "status": status,
        }

    # 6. Parse structured JSON response
    parsed_json = _extract_json_object(raw_text)

    if parsed_json and isinstance(parsed_json, dict):
        return {
            "summary": parsed_json.get(
                "summary",
                f"User exhibits elevated risk metrics (Score: {risk_score:.2f}).",
            ),
            "risk_drivers": parsed_json.get("risk_drivers", []),
            "recommended_action": parsed_json.get(
                "recommended_action",
                "Review recent user activity and verify authorization.",
            ),
            "urgency": parsed_json.get("urgency", risk_level),
            "raw_response": raw_text,
            "provider": provider_name,
            "model": model_name,
            "status": status if status == "mock" else "success",
            "usage": resp.get("usage", {}),
        }

    # 7. Fallback if JSON parsing fails: return raw text cleanly packaged
    logger.warning(
        "Failed to parse JSON from LLM response. Returning fallback structure."
    )
    return {
        "summary": raw_text[:300] if raw_text else "Risk analysis generated.",
        "risk_drivers": [],
        "recommended_action": "Review full incident log and verify user permissions.",
        "urgency": risk_level,
        "raw_response": raw_text,
        "provider": provider_name,
        "model": model_name,
        "status": "fallback_raw_text",
    }
