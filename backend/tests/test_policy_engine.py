"""Unit Tests for Policy Rule Engine."""

from policy_engine.engine import evaluate_policy_rules


def test_evaluate_policy_rules_triggers_action() -> None:
    """Tests that elevated metrics trigger expected policy rule actions."""
    metrics = {"usb_file_copy": 100}
    actions = evaluate_policy_rules(metrics)
    assert len(actions) == 1
    assert actions[0]["rule_id"] == "RULE-USB-EXFIL"
    assert actions[0]["action"] == "SIMULATED_REVOKE_USB_PERMISSIONS"
