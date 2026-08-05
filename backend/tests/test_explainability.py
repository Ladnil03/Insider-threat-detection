"""Unit Tests for SHAP Explainability Wrappers."""

from explainability.visualize import format_shap_summary_dict


def test_format_shap_summary_dict() -> None:
    """Tests formatting of SHAP attributions into sorted visual payload."""
    raw_shap = {
        "base_value": 0.1,
        "feature_attributions": {"usb_copy": 0.5, "after_hours": 0.2},
    }
    result = format_shap_summary_dict(raw_shap)
    assert result["base_value"] == 0.1
    assert result["features"][0]["feature"] == "usb_copy"
    assert result["features"][0]["attribution"] == 0.5
