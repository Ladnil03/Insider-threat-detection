"""Policy violation evaluation engine.

Iterates all defined rules against an activity stream and logs
triggered violations with severity.
"""


def evaluate_activity(activity: dict) -> list[dict]:
    """Run all policy rules against a single activity record.

    Args:
        activity: Dict with feature values and metadata.

    Returns:
        List of violation records, each with rule name, severity,
        and a human-readable reason. Empty list = no violations.

    Todo:
        Implement rule iteration in Week 5.

    """
    raise NotImplementedError("Week 5 — implement policy engine.")
