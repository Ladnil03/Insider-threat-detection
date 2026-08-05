"""Prompt Templates for LLM Threat Reasoning."""

from typing import Any, Dict

ANALYST_RECOMMENDATION_SYSTEM_PROMPT = """You are an expert Security Operations Center (SOC) Insider Threat Analyst assistant.
Given a user risk score, risk bucket, SHAP attribution details, and recent activity metrics, generate a concise plain-English summary:
1. Threat Summary: Explain why the activity flagged as risky.
2. Key Risk Drivers: Highlight the top 2-3 behavioral metrics according to SHAP attribution.
3. Recommended Action: Specific mitigation steps (e.g. revoke USB access, request supervisor review, isolate host).
"""


def build_analyst_prompt(
    user_id: str,
    risk_score: float,
    risk_level: str,
    shap_explanation: Dict[str, float],
    recent_activity: Dict[str, Any],
) -> str:
    """Builds formatted prompt for LLM recommendation inference.

    Args:
        user_id: Target user ID.
        risk_score: Combined risk score [0.0, 1.0].
        risk_level: Categorized risk bucket (e.g. HIGH, CRITICAL).
        shap_explanation: Dictionary of top SHAP feature contributions.
        recent_activity: Dictionary of metric counts for the observation period.

    Returns:
        Formatted prompt string.
    """
    return (
        f"User ID: {user_id}\n"
        f"Overall Risk Score: {risk_score:.2f} ({risk_level})\n"
        f"Top SHAP Feature Attributions: {shap_explanation}\n"
        f"Activity Metrics: {recent_activity}\n"
        "Provide your analysis and recommended action."
    )
