"""Unit Tests for Policy Rule Engine and Simulated Response Actions."""

from policy_engine.engine import evaluate_policy_rules
from policy_engine.rules import get_default_policy_rules


def test_get_default_policy_rules_catalogue() -> None:
    """Verifies that all 5 default policy rules are registered with required keys."""
    rules = get_default_policy_rules()
    assert len(rules) == 5
    expected_rule_ids = {
        "RULE-USB-EXFIL",
        "RULE-CRITICAL-SCORE",
        "RULE-AFTER-HOURS-SPIKE",
        "RULE-MASS-EXTERNAL-ATTACHMENT",
        "RULE-FLIGHT-RISK-JOB-HUNT",
    }
    actual_rule_ids = {r["rule_id"] for r in rules}
    assert actual_rule_ids == expected_rule_ids

    for rule in rules:
        assert "name" in rule
        assert "severity" in rule
        assert "condition" in rule
        assert "action" in rule
        assert "description" in rule


def test_rule_usb_exfil_triggers() -> None:
    """Tests that mass USB file transfers or 3-sigma spikes trigger USB revocation."""
    # Trigger via raw count
    actions1 = evaluate_policy_rules({"file_copy_usb": 60})
    assert any(a["rule_id"] == "RULE-USB-EXFIL" for a in actions1)
    assert actions1[0]["action"] == "SIMULATED_REVOKE_USB_PERMISSIONS"
    assert actions1[0]["severity"] == "CRITICAL"

    # Trigger via baseline deviation
    actions2 = evaluate_policy_rules({"file_copy_usb_baseline_dev": 3.5})
    assert any(a["rule_id"] == "RULE-USB-EXFIL" for a in actions2)


def test_rule_critical_score_triggers() -> None:
    """Tests that composite/model risk score >= 0.85 triggers mandatory supervisor alert."""
    actions = evaluate_policy_rules({"risk_score": 0.89})
    assert any(a["rule_id"] == "RULE-CRITICAL-SCORE" for a in actions)
    assert any(a["action"] == "SIMULATED_MANDATORY_SUPERVISOR_ALERT" for a in actions)


def test_rule_after_hours_spike_triggers() -> None:
    """Tests that off-hours logon surge triggers MFA challenge."""
    actions = evaluate_policy_rules({"logon_after_hours": 6})
    assert any(a["rule_id"] == "RULE-AFTER-HOURS-SPIKE" for a in actions)
    assert any(a["action"] == "SIMULATED_PROMPT_MFA_CHALLENGE" for a in actions)
    assert any(a["severity"] == "HIGH" for a in actions)


def test_rule_mass_external_attachment_triggers() -> None:
    """Tests that high-volume external emails with attachments trigger quarantine."""
    actions = evaluate_policy_rules(
        {"email_external_count": 15, "email_large_attachment_count": 4}
    )
    assert any(a["rule_id"] == "RULE-MASS-EXTERNAL-ATTACHMENT" for a in actions)
    assert any(a["action"] == "SIMULATED_QUARANTINE_OUTBOUND_EMAIL" for a in actions)


def test_rule_flight_risk_job_hunt_triggers() -> None:
    """Tests that job hunt activity spike triggers elevated monitoring."""
    actions = evaluate_policy_rules({"web_job_search_count": 12})
    assert any(a["rule_id"] == "RULE-FLIGHT-RISK-JOB-HUNT" for a in actions)
    assert any(a["action"] == "SIMULATED_ELEVATE_MONITORING_PRIORITY" for a in actions)
    assert any(a["severity"] == "MEDIUM" for a in actions)


def test_benign_activity_triggers_zero_actions() -> None:
    """Tests that normal baseline activity triggers zero automated actions."""
    benign_metrics = {
        "logon_count": 2,
        "logon_after_hours": 0,
        "file_copy_usb": 0,
        "email_external_count": 2,
        "email_large_attachment_count": 0,
        "web_job_search_count": 0,
        "risk_score": 0.15,
        "sai_score": 0.05,
    }
    actions = evaluate_policy_rules(benign_metrics)
    assert len(actions) == 0
