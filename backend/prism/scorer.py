"""PRISM rule-based risk scorer.

Computes per-feature sub-scores and a weighted total score for each
activity record. Sub-score definitions follow the PRISM methodology
from the base paper (Koli et al.).
"""


def compute_risk_score(activity: dict) -> float:
    """Compute weighted PRISM risk score for a single activity.

    Args:
        activity: Dictionary with feature values and metadata.

    Returns:
        Float risk score in [0, 1].

    Todo:
        Implement sub-score logic in Week 3.

    """
    raise NotImplementedError("Week 3 — implement PRISM sub-scores.")
