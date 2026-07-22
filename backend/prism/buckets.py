"""Risk-bucketing thresholds for PRISM scores.

Maps continuous risk scores to discrete severity labels
(e.g. low / medium / high / critical) for display and policy
triggering.
"""


def score_to_bucket(score: float) -> str:
    """Convert a numeric risk score to a severity label.

    Args:
        score: Risk score in [0, 1].

    Returns:
        One of "low", "medium", "high", "critical".

    Todo:
        Define threshold constants (Week 3).

    """
    raise NotImplementedError("Week 3 — implement bucket thresholds.")
