"""Live Testing Script for OpenIRM Groq LLM Recommendation Service.

Can be run directly via CLI to test real Groq API inference (if GROQ_API_KEY is set)
or verify mock fallback behavior.

Usage:
    python -m llm_service.live_test
"""

import os
import sys
from pathlib import Path

# Add backend to path if run standalone
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm_service.providers.factory import get_llm_provider
from llm_service.recommend import get_threat_recommendation


def run_live_test() -> None:
    """Executes a realistic insider threat scenario against the active LLM provider."""
    print("=" * 70)
    print("  OpenIRM LLM Recommendation Service - Live Verification Test")
    print("=" * 70)

    has_key = bool(os.getenv("GROQ_API_KEY", "").strip())
    print(
        f"[*] GROQ_API_KEY configured: {'YES (Live Groq Inference)' if has_key else 'NO (Deterministic Mock Fallback)'}"
    )

    provider = get_llm_provider()
    print(f"[*] Active Provider: {type(provider).__name__}")
    print(f"[*] Target Model: {getattr(provider, 'model', 'N/A')}")
    print("-" * 70)

    # Realistic sample insider threat scenario: Mass USB Exfiltration after hours
    sample_scenario = {
        "user_id": "ACM2278",
        "user_role": "Senior Systems Engineer (Elevated Privileges)",
        "risk_score": 0.895,
        "risk_level": "CRITICAL",
        "prism_score": 0.780,
        "sai_score": 0.912,
        "shap_explanation": {
            "top_risk_drivers": [
                {
                    "feature_key": "file_copy_usb_baseline_dev",
                    "feature_name": "Mass USB File Exfiltration Spike (30-Day Z-Score)",
                    "shap_value": 0.482,
                    "percentage_contribution": 52.4,
                },
                {
                    "feature_key": "logon_after_hours",
                    "feature_name": "Off-Hours Logons (Night/Weekend)",
                    "shap_value": 0.261,
                    "percentage_contribution": 28.4,
                },
                {
                    "feature_key": "email_large_attachment_count",
                    "feature_name": "Large Data Attachment to External Domains",
                    "shap_value": 0.115,
                    "percentage_contribution": 12.5,
                },
            ]
        },
        "recent_activity": {
            "logon_after_hours": 8,
            "file_copy_usb": 142,
            "email_external_count": 24,
            "email_large_attachment_count": 5,
            "device_connect_count": 4,
        },
        "policy_violations": [
            {
                "rule_id": "RULE-USB-EXFIL",
                "rule_name": "Mass USB Removable Media Exfiltration",
                "severity": "CRITICAL",
                "action": "SIMULATED_REVOKE_USB_PERMISSIONS",
            },
            {
                "rule_id": "RULE-CRITICAL-SCORE",
                "rule_name": "Critical Risk Score Threshold Breach",
                "severity": "CRITICAL",
                "action": "SIMULATED_MANDATORY_SUPERVISOR_ALERT",
            },
        ],
    }

    print("[*] Dispatching recommendation request...")
    recommendation = get_threat_recommendation(
        user_id=sample_scenario["user_id"],
        risk_score=sample_scenario["risk_score"],
        risk_level=sample_scenario["risk_level"],
        prism_score=sample_scenario["prism_score"],
        sai_score=sample_scenario["sai_score"],
        shap_explanation=sample_scenario["shap_explanation"],
        recent_activity=sample_scenario["recent_activity"],
        user_role=sample_scenario["user_role"],
        policy_violations=sample_scenario["policy_violations"],
        provider=provider,
    )

    print("\n[+] STRUCTURED RECOMMENDATION RECEIVED:")
    print(f"Status: {recommendation.get('status')}")
    print(f"Urgency: {recommendation.get('urgency')}")
    print(f"\n--- Executive Threat Summary ---\n{recommendation.get('summary')}")
    print("\n--- Key Behavioral Risk Drivers ---")
    for driver in recommendation.get("risk_drivers", []):
        print(
            f"  * [{driver.get('impact', 'INFO')}] {driver.get('feature')}: {driver.get('description')}"
        )
    print(
        f"\n--- Recommended SOC Action ---\n{recommendation.get('recommended_action')}"
    )

    if "usage" in recommendation and recommendation["usage"]:
        print(
            f"\n[Token Usage] Total Tokens: {recommendation['usage'].get('total_tokens')}"
        )

    print("=" * 70)


if __name__ == "__main__":
    run_live_test()
