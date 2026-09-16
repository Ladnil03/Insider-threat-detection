"""Policy Engine Trigger Evaluation Logic."""

from typing import Any, Dict, List, Optional

from policy_engine.rules import get_default_policy_rules


def evaluate_policy_rules(
    user_metrics: Dict[str, Any],
    rules: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Evaluates user metrics against policy rules and returns triggered actions.

    Args:
        user_metrics: Dictionary of user risk and activity metrics.
        rules: Optional list of rules (defaults to get_default_policy_rules()).

    Returns:
        List of triggered action event dicts including rule_id, rule_name, severity, action, and description.
    """
    if rules is None:
        rules = get_default_policy_rules()

    triggered_actions = []

    for rule in rules:
        try:
            if rule["condition"](user_metrics):
                triggered_actions.append(
                    {
                        "rule_id": rule["rule_id"],
                        "rule_name": rule["name"],
                        "severity": rule.get("severity", "MEDIUM"),
                        "action": rule["action"],
                        "description": rule.get("description", ""),
                    }
                )
        except Exception:
            # Handle potential type errors or missing metrics safely without crashing
            continue

    return triggered_actions
