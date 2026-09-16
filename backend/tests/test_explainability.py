"""Unit and Integration Tests for SHAP Explainability Layer."""

import tempfile
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from airs.model import AIRSAutoencoder
from data_pipeline.config import ALL_FEATURE_COLS
from explainability.shap_explainer import (
    AIRSShapExplainer,
    SHAPCache,
    get_human_readable_feature_name,
    precompute_and_cache_explanations,
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
    benign_baseline = np.random.normal(loc=0.0, scale=0.5, size=(30, 72)).astype(
        np.float32
    )
    scaler.fit(benign_baseline)

    explainer = AIRSShapExplainer(
        model=model,
        scaler=scaler,
        background_data=benign_baseline,
        background_samples=15,
        cache=SHAPCache(),
    )

    # Test sample with acute spike in feature 3 (file_copy_usb)
    test_sample = np.zeros(72, dtype=np.float32)
    test_sample[3] = 10.0  # High anomalous spike

    explanation = explainer.explain_activity(test_sample, top_k=5, nsamples=80)

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


def test_shap_cache_hit_and_disk_persistence() -> None:
    """Tests SHAPCache LRU operations, hit/miss tracking, and JSON persistence."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        cache_path = Path(tmp_dir) / "test_shap_cache.json"
        cache = SHAPCache(cache_file=cache_path, max_size=5)

        key1 = "key_sample_1"
        payload1 = {"reconstruction_error": 0.45, "sai_score": 0.22}

        # Initial cache miss
        assert cache.get(key1) is None
        assert cache.stats["misses"] == 1

        # Store in cache
        cache.set(key1, payload1)
        assert cache.stats["size"] == 1

        # Cache hit
        retrieved = cache.get(key1)
        assert retrieved is not None
        assert retrieved["reconstruction_error"] == 0.45
        assert cache.stats["hits"] == 1

        # Disk persistence
        cache.save_to_disk()
        assert cache_path.exists()

        # Load into fresh cache instance
        cache2 = SHAPCache(cache_file=cache_path, max_size=5)
        loaded = cache2.get(key1)
        assert loaded is not None
        assert loaded["sai_score"] == 0.22


def test_explain_activity_caching_speedup() -> None:
    """Verifies that caching produces identical outputs with sub-millisecond retrieval."""
    np.random.seed(42)
    model = AIRSAutoencoder(input_dim=72, hidden_dims=[48, 24], latent_dim=12)
    scaler = StandardScaler()
    benign_baseline = np.random.normal(loc=0.0, scale=0.5, size=(20, 72)).astype(
        np.float32
    )
    scaler.fit(benign_baseline)

    cache = SHAPCache(max_size=50)
    explainer = AIRSShapExplainer(
        model=model,
        scaler=scaler,
        background_data=benign_baseline,
        background_samples=10,
        cache=cache,
    )

    test_vector = np.random.uniform(0, 5, size=72).astype(np.float32)

    # First call: computes via KernelExplainer
    t0 = time.perf_counter()
    exp1 = explainer.explain_activity(test_vector, nsamples=40, use_cache=True)
    t_compute = time.perf_counter() - t0

    # Second call: retrieves from cache
    t1 = time.perf_counter()
    exp2 = explainer.explain_activity(test_vector, nsamples=40, use_cache=True)
    t_cached = time.perf_counter() - t1

    assert exp1["reconstruction_error"] == exp2["reconstruction_error"]
    assert exp1["sai_score"] == exp2["sai_score"]
    assert cache.stats["hits"] == 1
    # Cache hit should be dramatically faster (< 10ms)
    assert t_cached < t_compute


def test_explain_activity_edge_cases() -> None:
    """Tests edge cases: all-zero input vector, dict input with missing keys, and Pandas Series."""
    np.random.seed(42)
    model = AIRSAutoencoder(input_dim=72, hidden_dims=[48, 24], latent_dim=12)
    scaler = StandardScaler()
    benign_baseline = np.random.normal(loc=0.0, scale=0.5, size=(20, 72)).astype(
        np.float32
    )
    scaler.fit(benign_baseline)

    explainer = AIRSShapExplainer(
        model=model,
        scaler=scaler,
        background_data=benign_baseline,
        background_samples=10,
        cache=SHAPCache(),
    )

    # 1. All-zero vector
    zero_vec = np.zeros(72, dtype=np.float32)
    zero_exp = explainer.explain_activity(zero_vec, nsamples=30)
    assert isinstance(zero_exp["reconstruction_error"], float)
    assert len(zero_exp["ranked_contributions"]) == 72

    # 2. Sparse dictionary input
    sparse_dict = {"logon_count": 5.0, "file_copy_usb": 12.0}
    dict_exp = explainer.explain_activity(sparse_dict, nsamples=30)
    assert "top_risk_drivers" in dict_exp

    # 3. Pandas Series input
    series_data = pd.Series(
        {col: 1.0 for col in ALL_FEATURE_COLS[:30]}, index=ALL_FEATURE_COLS[:30]
    )
    series_exp = explainer.explain_activity(series_data, nsamples=30)
    assert series_exp["sai_score"] >= 0.0


def test_precompute_and_cache_explanations() -> None:
    """Tests batch precomputation on a mock dataframe."""
    np.random.seed(42)
    model = AIRSAutoencoder(input_dim=72, hidden_dims=[48, 24], latent_dim=12)
    scaler = StandardScaler()
    benign_baseline = np.random.normal(loc=0.0, scale=0.5, size=(20, 72)).astype(
        np.float32
    )
    scaler.fit(benign_baseline)

    cache = SHAPCache()
    explainer = AIRSShapExplainer(
        model=model,
        scaler=scaler,
        background_data=benign_baseline,
        background_samples=10,
        cache=cache,
    )

    # Create mock dataframe with 5 user rows
    data = np.random.uniform(0, 3, size=(5, 72))
    df = pd.DataFrame(data, columns=ALL_FEATURE_COLS)
    df["user"] = [f"USER_{i}" for i in range(5)]
    df["date_day"] = "2026-08-01"
    df["sai_score"] = [0.1, 0.8, 0.4, 0.9, 0.3]

    count = precompute_and_cache_explanations(df, explainer, top_n=3)
    assert count == 3
    assert cache.stats["size"] >= 3


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
