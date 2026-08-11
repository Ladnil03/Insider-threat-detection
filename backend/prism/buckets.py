"""Risk bucketing thresholds and Min-Max normalization for PRISM."""

from typing import Dict, Literal, Union, overload

import numpy as np
import pandas as pd

RiskLevel = Literal["LOW", "MODERATE", "HIGH", "CRITICAL"]

# Default thresholds matching paper and weights.yaml
DEFAULT_THRESHOLDS: Dict[str, float] = {
    "low_max": 0.30,
    "moderate_max": 0.60,
    "high_max": 0.80,
}


@overload
def min_max_normalize(
    score: float, min_val: float = 0.0, max_val: float = 1.0
) -> float: ...


@overload
def min_max_normalize(
    score: np.ndarray, min_val: float = 0.0, max_val: float = 1.0
) -> np.ndarray: ...


@overload
def min_max_normalize(
    score: pd.Series, min_val: float = 0.0, max_val: float = 1.0
) -> pd.Series: ...


def min_max_normalize(
    score: Union[float, np.ndarray, pd.Series],
    min_val: float = 0.0,
    max_val: float = 1.0,
) -> Union[float, np.ndarray, pd.Series]:
    """Applies Min-Max scaling to map raw risk scores to [0.0, 1.0].

    Formula: S_norm = (S - min_val) / (max_val - min_val), clipped to [0.0, 1.0].

    Args:
        score: Raw numerical score or array of scores.
        min_val: Expected or empirical minimum raw score.
        max_val: Expected or empirical maximum raw score.

    Returns:
        Normalized score(s) bounded strictly between 0.0 and 1.0.
    """
    if max_val == min_val:
        if isinstance(score, (np.ndarray, pd.Series)):
            return np.zeros_like(score, dtype=float)
        return 0.0

    normalized = (score - min_val) / (max_val - min_val)
    if isinstance(normalized, (np.ndarray, pd.Series)):
        return np.clip(normalized, 0.0, 1.0)
    return float(np.clip(normalized, 0.0, 1.0))


def classify_risk_score(
    score: float, thresholds: Union[Dict[str, float], None] = None
) -> RiskLevel:
    """Categorizes a normalized risk score [0.0, 1.0] into a risk bucket.

    Args:
        score: Floating point risk score between 0.0 and 1.0.
        thresholds: Optional dictionary defining 'low_max', 'moderate_max', 'high_max'.

    Returns:
        Risk level category string: LOW, MODERATE, HIGH, or CRITICAL.
    """
    t = thresholds or DEFAULT_THRESHOLDS
    low_max = t.get("low_max", 0.30)
    moderate_max = t.get("moderate_max", 0.60)
    high_max = t.get("high_max", 0.80)

    if score < low_max:
        return "LOW"
    if score < moderate_max:
        return "MODERATE"
    if score < high_max:
        return "HIGH"
    return "CRITICAL"
