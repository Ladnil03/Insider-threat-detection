"""Unit and Regression Tests for PRISM Rule Engine."""

import math

import numpy as np
import pandas as pd

from prism.batch_scorer import score_dataframe
from prism.buckets import classify_risk_score, min_max_normalize
from prism.scorer import (
    activity_type_score,
    application_context_score,
    business_hours_score,
    calculate_prism_score,
    cumulative_activity_score,
    device_compliance_score,
    ip_score,
    user_privilege_score,
)


def test_user_privilege_score() -> None:
    """Tests user privilege sub-score Sp mappings."""
    assert user_privilege_score("domain_admin") == 1.0
    assert user_privilege_score("admin") == 1.0
    assert user_privilege_score("it_admin") == 0.6
    assert user_privilege_score("analyst") == 0.3
    assert user_privilege_score("low_privilege") == 0.1
    assert user_privilege_score("employee") == 0.1
    assert user_privilege_score("unknown_role") == 0.2


def test_activity_type_score() -> None:
    """Tests activity type sub-score SA mappings."""
    assert activity_type_score("usb_exfiltration") == 1.0
    assert activity_type_score("exfiltration") == 1.0
    assert activity_type_score("sensitive_file_access") == 0.7
    assert activity_type_score("file_move") == 0.3
    assert activity_type_score("web_visit") == 0.2
    assert activity_type_score("logon") == 0.1


def test_application_context_score() -> None:
    """Tests application context sub-score SC mappings."""
    assert application_context_score("personal_webmail") == 1.0
    assert application_context_score("usb_storage") == 0.8
    assert application_context_score("sharepoint") == 0.4
    assert application_context_score("intranet") == 0.2
    assert application_context_score("general_app") == 0.1


def test_ip_score() -> None:
    """Tests IP network origin sub-score SIP logic."""
    known_ips = ["10.0.0.1", "10.0.0.2"]
    assert ip_score("10.0.0.1", known_ips) == 0.0
    assert ip_score("192.168.1.100", known_ips) == 0.5
    assert ip_score("tor_node") == 1.0
    assert ip_score("192.168.1.100") == 0.5


def test_business_hours_score() -> None:
    """Tests business hours sub-score SB time parsing."""
    # Wednesday 10:00 AM (business hours)
    assert business_hours_score("2026-08-05 10:00:00") == 0.0
    # Wednesday 9:00 PM (off hours)
    assert business_hours_score("2026-08-05 21:00:00") == 0.6
    # Sunday (weekend off hours)
    assert business_hours_score("2026-08-09 12:00:00") == 0.6
    # String helpers
    assert business_hours_score("business_hours") == 0.0
    assert business_hours_score("off_hours") == 0.6


def test_device_compliance_score() -> None:
    """Tests device compliance sub-score SD logic."""
    compliant_list = ["DEV-001", "DEV-002"]
    assert device_compliance_score("DEV-001", compliant_list) == 0.0
    assert device_compliance_score("compliant") == 0.0
    assert device_compliance_score("DEV-UNKNOWN", compliant_list) == 0.7


def test_cumulative_activity_score() -> None:
    """Tests cumulative activity volume sub-score SCA scaling."""
    assert cumulative_activity_score(0) == 0.0
    assert cumulative_activity_score(5) == 0.25
    assert cumulative_activity_score(20) == 1.0
    assert cumulative_activity_score(50) == 1.0  # saturation capped at 1.0
    assert cumulative_activity_score([{}, {}, {}]) == 0.15


def test_paper_worked_example_regression() -> None:
    """Regression test verifying the paper's worked example score.

    Worked Example Details from Paper:
    - User Role: low-privilege employee (Sp = 0.1)
    - Activity Type: file move (SA = 0.3)
    - Application Context: SharePoint (SC = 0.4)
    - IP Origin: unknown IP (SIP = 0.5)
    - Business Hours: off-hours activity (SB = 0.6)
    - Device: non-compliant device (SD = 0.7)
    - Cumulative Volume: 5 files moved (SCA = 0.25)

    Paper Formula & Weights:
    Wp=0.20, WA=0.15, WC=0.15, WIP=0.15, WB=0.15, WD=0.10, WCA=0.10
    R = 0.20(0.1) + 0.15(0.3) + 0.15(0.4) + 0.15(0.5) + 0.15(0.6) + 0.10(0.7) + 0.10(0.25)
    R = 0.020 + 0.045 + 0.060 + 0.075 + 0.090 + 0.070 + 0.025 = 0.385

    Target score: ~0.385 (Risk Bucket: MODERATE)
    """
    paper_weights = {
        "user_privilege": 0.20,
        "activity_type": 0.15,
        "application_context": 0.15,
        "ip_address": 0.15,
        "business_hours": 0.15,
        "device_compliance": 0.10,
        "cumulative_activity": 0.10,
    }

    result = calculate_prism_score(
        user_role="low_privilege",
        activity_type="file_move",
        app_name="sharepoint",
        ip_address="192.168.1.100",
        known_ips=["10.0.0.1"],
        timestamp="2026-08-05 21:00:00",  # off-hours
        device_id="DEV-UNKNOWN",
        compliant_devices=["DEV-001"],
        activity_window=5,
        custom_weights=paper_weights,
    )

    assert math.isclose(result["raw_score"], 0.385, abs_tol=0.005)
    assert math.isclose(result["prism_score"], 0.385, abs_tol=0.005)
    assert result["risk_level"] == "MODERATE"


def test_min_max_normalize() -> None:
    """Tests Min-Max normalization utility function."""
    assert min_max_normalize(0.5, 0.0, 1.0) == 0.5
    assert min_max_normalize(5.0, 0.0, 10.0) == 0.5
    assert min_max_normalize(-1.0, 0.0, 1.0) == 0.0  # clipped min
    assert min_max_normalize(2.0, 0.0, 1.0) == 1.0  # clipped max

    arr = np.array([0.0, 5.0, 10.0])
    normalized_arr = min_max_normalize(arr, 0.0, 10.0)
    np.testing.assert_array_almost_equal(normalized_arr, np.array([0.0, 0.5, 1.0]))


def test_classify_risk_score_levels() -> None:
    """Tests risk score categorization thresholds."""
    assert classify_risk_score(0.15) == "LOW"
    assert classify_risk_score(0.45) == "MODERATE"
    assert classify_risk_score(0.70) == "HIGH"
    assert classify_risk_score(0.90) == "CRITICAL"


def test_batch_score_dataframe() -> None:
    """Tests batch scoring over synthetic pandas DataFrame."""
    synthetic_data = pd.DataFrame(
        [
            {
                "user": "benign_user",
                "role": "employee",
                "logon_after_hours": 0.0,
                "file_copy_usb": 0.0,
                "file_sensitive_access": 0.0,
                "email_external_count": 0.0,
                "web_job_search_count": 0.0,
                "device_connect_count": 0.0,
                "is_malicious": 0,
            },
            {
                "user": "malicious_user",
                "role": "employee",
                "logon_after_hours": 5.0,
                "file_copy_usb": 12.0,
                "file_sensitive_access": 4.0,
                "email_external_count": 8.0,
                "web_job_search_count": 3.0,
                "device_connect_count": 2.0,
                "is_malicious": 1,
            },
        ]
    )

    scored = score_dataframe(synthetic_data)
    assert "prism_score" in scored.columns
    assert "prism_risk_level" in scored.columns

    benign_score = scored.loc[0, "prism_score"]
    malicious_score = scored.loc[1, "prism_score"]

    assert malicious_score > benign_score
    assert scored.loc[0, "prism_risk_level"] == "LOW"
    assert scored.loc[1, "prism_risk_level"] in ("HIGH", "CRITICAL")
