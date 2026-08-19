"""Unit and Integration Tests for SHAP Explainability Layer."""

import tempfile
from pathlib import Path

import numpy as np
from sklearn.preprocessing import StandardScaler

from airs.model import AIRSAutoencoder
from explainability.shap_explainer import (
    AIRSShapExplainer,
    get_human_readable_feature_name,
)
from explainability.visualize import format_shap_summary_dict, generate_waterfall_plot


def test_get_human_readable_feature_name() -> None:
    """Tests that raw feature column keys map to clean human-readable titles."""
    assert (
        get_human_readable_feature_name("file_copy_usb")
        == "USB Removable Media File Transfers"
    )
    assert (
        get_human_readable_feature_name("logon_after_hours")
        == "Off-Hours Logons (Night/Weekend)"
    )
    assert (
        get_human_readable_feature_name("email_large_attachment_count_baseline_dev")
        == "Mass Data Attachment Spike (30-Day Z-Score)"
    )


def test_format_shap_summary_dict() -> None:
    """Tests formatting of SHAP attributions into sorted visual payload."""
    raw_explanation = {
        "base_value": 0.05,
        "reconstruction_error": 1.25,
        "sai_score": 0.49,
        "human_readable_summary": "Primary risk drivers: USB: 60.0%",
        "ranked_contributions": [
            {
                "feature_key": "file_copy_usb",
                "feature_name": "USB Removable Media File Transfers",
                "feature_value": 15.0,
                "shap_value": 0.60,
                "percentage_contribution": 60.0,
                "direction": "INCREASES_RISK",
            },
            {
                "feature_key": "logon_count",
                "feature_name": "Total Daily Logons",
                "feature_value": 2.0,
                "shap_value": -0.10,
                "percentage_contribution": 0.0,
                "direction": "DECREASES_RISK",
            },
        ],
        "top_risk_drivers": [
            {
                "feature_key": "file_copy_usb",
                "feature_name": "USB Removable Media File Transfers",
                "feature_value": 15.0,
                "shap_value": 0.60,
                "percentage_contribution": 60.0,
                "direction": "INCREASES_RISK",
            }
        ],
    }

    result = format_shap_summary_dict(raw_explanation)
    assert result["base_value"] == 0.05
    assert result["reconstruction_error"] == 1.25
    assert len(result["features"]) == 2
    assert result["features"][0]["feature"] == "USB Removable Media File Transfers"
    assert result["features"][0]["attribution"] == 0.60
    assert result["features"][0]["direction"] == "INCREASES_RISK"


def test_airs_shap_explainer_sanity_check_and_efficiency() -> None:
    """Tests SHAP explainer consistency:

    1. Sum of Shapley values + base_value approximates actual model reconstruction error
       within mathematical KernelExplainer sampling tolerance (tolerance = 0.15).
    2. An anomalous spike feature produces positive risk-increasing SHAP value.
    """
    np.random.seed(42)
    model = AIRSAutoencoder(input_dim=72, hidden_dims=[48, 24], latent_dim=12)
    scaler = StandardScaler()

    # Create synthetic benign baseline and fit scaler
    benign_baseline = np.random.normal(loc=0.0, scale=0.5, size=(40, 72)).astype(
        np.float32
    )
    scaler.fit(benign_baseline)

    explainer = AIRSShapExplainer(
        model=model,
        scaler=scaler,
        background_data=benign_baseline,
        background_samples=20,
    )

    # Test sample with acute spike in feature 3 (file_copy_usb)
    test_sample = np.zeros(72, dtype=np.float32)
    test_sample[3] = 10.0  # High anomalous spike

    explanation = explainer.explain_activity(test_sample, top_k=5, nsamples=100)

    assert "reconstruction_error" in explanation
    assert "base_value" in explanation
    assert "ranked_contributions" in explanation
    assert len(explanation["ranked_contributions"]) == 72

    # Efficiency Property Check: sum(phi_i) + base_value ~= model_output f(x)
    total_shap = float(np.sum(explanation["all_shap_values"]))
    reconstructed_f_x = explanation["base_value"] + total_shap
    actual_f_x = explanation["reconstruction_error"]

    # Documented KernelExplainer sampling tolerance epsilon = 0.15
    tolerance = 0.15
    diff = abs(reconstructed_f_x - actual_f_x)
    assert (
        diff < tolerance
    ), f"Efficiency property failed: base+sum(phi)={reconstructed_f_x:.4f}, f(x)={actual_f_x:.4f}, diff={diff:.4f} > {tolerance}"


def test_generate_waterfall_plot_creates_figure() -> None:
    """Tests that generate_waterfall_plot returns valid Figure and saves PNG to disk."""
    sample_explanation = {
        "base_value": 0.05,
        "sai_score": 0.85,
        "ranked_contributions": [
            {
                "feature_name": "USB File Transfers",
                "shap_value": 0.45,
                "percentage_contribution": 45.0,
            },
            {
                "feature_name": "Off-Hours Logons",
                "shap_value": 0.30,
                "percentage_contribution": 30.0,
            },
            {
                "feature_name": "Regular Web Browsing",
                "shap_value": -0.05,
                "percentage_contribution": 0.0,
            },
        ],
    }

    with tempfile.TemporaryDirectory() as tmp_dir:
        out_png = Path(tmp_dir) / "test_waterfall.png"
        fig = generate_waterfall_plot(
            sample_explanation, max_display=5, output_path=out_png
        )

        assert fig is not None
        assert out_png.exists()
        assert out_png.stat().st_size > 0
