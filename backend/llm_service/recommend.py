"""Orchestrates LLM recommendation generation.

Builds a prompt from (score + SHAP + context), calls the active
provider, parses and returns the recommendation text.
"""


def generate_recommendation(
    risk_score: float,
    severity_bucket: str,
    shap_summary: str,
    user_history_summary: str,
) -> str:
    """Build prompt and call the active LLM provider for a recommendation.

    Args:
        risk_score: Numeric risk score [0, 1].
        severity_bucket: "low" | "medium" | "high" | "critical".
        shap_summary: Human-readable SHAP attribution summary.
        user_history_summary: Recent activity summary for the user.

    Returns:
        Plain-text analyst recommendation.

    Todo:
        Wire up provider selection and API call in Week 7.

    """
    raise NotImplementedError("Week 7 — implement recommendation orchestration.")
