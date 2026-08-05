"""Unit Tests for PRISM Rule Engine."""

from prism.buckets import classify_risk_score
from prism.scorer import calculate_prism_score


def test_classify_risk_score_levels() -> None:
    """Tests risk score categorization thresholds."""
    assert classify_risk_score(0.1) == "LOW"
    assert classify_risk_score(0.4) == "MEDIUM"
    assert classify_risk_score(0.7) == "HIGH"
    assert classify_risk_score(0.9) == "CRITICAL"


def test_calculate_prism_score_returns_expected_keys() -> None:
    """Tests that calculate_prism_score produces expected response structure."""
    result = calculate_prism_score({"after_hours_logon": 1.0})
    assert "raw_score" in result
    assert "prism_score" in result
    assert "risk_level" in result
