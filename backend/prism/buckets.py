"""Risk bucketing thresholds for categorization."""

from typing import Literal

RiskLevel = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]


def classify_risk_score(score: float) -> RiskLevel:
    """Categorizes a normalized risk score [0.0, 1.0] into a risk bucket.

    Args:
        score: Floating point risk score between 0.0 and 1.0.

    Returns:
        Risk level category string.
    """
    if score >= 0.8:
        return "CRITICAL"
    if score >= 0.6:
        return "HIGH"
    if score >= 0.3:
        return "MEDIUM"
    return "LOW"
