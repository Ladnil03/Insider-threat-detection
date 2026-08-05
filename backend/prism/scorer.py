"""PRISM Rule-Based Risk Sub-Score Calculator."""

from typing import Any, Dict

from prism.buckets import RiskLevel, classify_risk_score


def calculate_prism_score(activity_features: Dict[str, float]) -> Dict[str, Any]:
    """Calculates weighted PRISM rule-based score from daily user features.

    Args:
        activity_features: Dictionary of user activity metric counts.

    Returns:
        Dictionary containing raw score, normalized score, and risk level.
    """
    total_score: float = 0.0
    # Stub computation
    normalized_score: float = min(1.0, max(0.0, total_score))
    risk_level: RiskLevel = classify_risk_score(normalized_score)

    return {
        "raw_score": total_score,
        "prism_score": normalized_score,
        "risk_level": risk_level,
    }
