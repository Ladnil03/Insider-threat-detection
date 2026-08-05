"""Policy Engine Trigger Evaluation Logic."""

from typing import Any, Dict, List

from policy_engine.rules import get_default_policy_rules


def evaluate_policy_rules(user_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Evaluates user metrics against policy rules and returns triggered actions.

    Args:
        user_metrics: Dictionary of user risk and activity metrics.

    Returns:
        List of triggered action event dicts.
    """
    rules = get_default_policy_rules()
    triggered_actions = []

    for rule in rules:
        if rule["condition"](user_metrics):
            triggered_actions.append(
                {
                    "rule_id": rule["rule_id"],
                    "rule_name": rule["name"],
                    "action": rule["action"],
                }
            )
    return triggered_actions
