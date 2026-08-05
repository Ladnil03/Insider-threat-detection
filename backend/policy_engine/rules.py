"""Policy Rule Definitions."""

from typing import Any, Dict, List


def get_default_policy_rules() -> List[Dict[str, Any]]:
    """Returns baseline policy rules mapping threshold conditions to automated actions.

    Returns:
        List of rule dictionaries.
    """
    return [
        {
            "rule_id": "RULE-USB-EXFIL",
            "name": "Mass USB Copy Detection",
            "condition": lambda metrics: metrics.get("usb_file_copy", 0) > 50,
            "action": "SIMULATED_REVOKE_USB_PERMISSIONS",
        },
        {
            "rule_id": "RULE-CRITICAL-SCORE",
            "name": "Critical Risk Score Breach",
            "condition": lambda metrics: metrics.get("risk_score", 0.0) >= 0.85,
            "action": "SIMULATED_MANDATORY_SUPERVISOR_ALERT",
        },
    ]
