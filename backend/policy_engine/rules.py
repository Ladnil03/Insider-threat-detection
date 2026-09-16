"""Policy Rule Definitions for OpenIRM Automated Response Simulation.

Maps behavioral anomalies and composite risk scores to automated enterprise remediation actions.
Addresses CERT insider threat scenarios (USB exfiltration, privilege abuse, flight risk, data leakage).
"""

from typing import Any, Dict, List


def get_default_policy_rules() -> List[Dict[str, Any]]:
    """Returns baseline policy rules mapping threshold conditions to automated actions.

    Returns:
        List of rule dictionaries containing rule_id, name, severity, condition callable,
        and simulated action descriptor.
    """
    return [
        {
            "rule_id": "RULE-USB-EXFIL",
            "name": "Mass USB Removable Media Exfiltration",
            "severity": "CRITICAL",
            "condition": lambda m: (
                m.get("file_copy_usb", 0) > 50
                or m.get("file_copy_usb_baseline_dev", 0.0) >= 3.0
            ),
            "action": "SIMULATED_REVOKE_USB_PERMISSIONS",
            "description": "Triggered when user copies >50 files to USB or exhibits a 3-sigma exfiltration surge.",
        },
        {
            "rule_id": "RULE-CRITICAL-SCORE",
            "name": "Critical Risk Score Threshold Breach",
            "severity": "CRITICAL",
            "condition": lambda m: (
                m.get("risk_score", 0.0) >= 0.85
                or m.get("sai_score", 0.0) >= 0.85
                or m.get("ensemble_score", 0.0) >= 0.85
            ),
            "action": "SIMULATED_MANDATORY_SUPERVISOR_ALERT",
            "description": "Triggered when composite or model risk score breaches critical 0.85 threshold.",
        },
        {
            "rule_id": "RULE-AFTER-HOURS-SPIKE",
            "name": "Abnormal Off-Hours Logon Surge",
            "severity": "HIGH",
            "condition": lambda m: (
                m.get("logon_after_hours", 0) >= 5
                or m.get("logon_after_hours_baseline_dev", 0.0) >= 3.0
            ),
            "action": "SIMULATED_PROMPT_MFA_CHALLENGE",
            "description": "Triggered when repeated night/weekend logons or 3-sigma off-hours deviation is detected.",
        },
        {
            "rule_id": "RULE-MASS-EXTERNAL-ATTACHMENT",
            "name": "Large Data Attachment to External Domains",
            "severity": "HIGH",
            "condition": lambda m: (
                m.get("email_external_count", 0) >= 10
                and m.get("email_large_attachment_count", 0) >= 3
            )
            or m.get("email_large_attachment_count_baseline_dev", 0.0) >= 3.0,
            "action": "SIMULATED_QUARANTINE_OUTBOUND_EMAIL",
            "description": "Triggered when high-volume external emails include multiple large file attachments.",
        },
        {
            "rule_id": "RULE-FLIGHT-RISK-JOB-HUNT",
            "name": "Flight Risk Job Search Activity Surge",
            "severity": "MEDIUM",
            "condition": lambda m: (
                m.get("web_job_search_count", 0) >= 10
                or m.get("web_job_search_count_baseline_dev", 0.0) >= 3.0
            ),
            "action": "SIMULATED_ELEVATE_MONITORING_PRIORITY",
            "description": "Triggered when user engages in intensive job search activity exceeding baseline profile.",
        },
    ]
