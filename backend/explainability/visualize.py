"""Visualization Helpers for SHAP Summary, Waterfall, and Force Attribution Plots."""

from pathlib import Path
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np
import shap


def format_shap_summary_dict(shap_result: Dict[str, Any]) -> Dict[str, Any]:
    """Formats raw SHAP output into a clean JSON-serializable structure for frontend rendering.

    Args:
        shap_result: Output from explain_activity.

    Returns:
        Structured chart payload with sorted feature importances and human-readable names.
    """
    ranked = shap_result.get("ranked_contributions", [])
    top_drivers = shap_result.get("top_risk_drivers", [])

    return {
        "base_value": shap_result.get("base_value", 0.0),
        "reconstruction_error": shap_result.get("reconstruction_error", 0.0),
        "sai_score": shap_result.get("sai_score", 0.0),
        "human_readable_summary": shap_result.get("human_readable_summary", ""),
        "top_risk_drivers": top_drivers,
        "features": [
            {
                "feature": c.get("feature_name", c.get("feature_key", "Unknown")),
                "raw_key": c.get("feature_key", ""),
                "attribution": c.get("shap_value", 0.0),
                "value": c.get("feature_value", 0.0),
                "percentage": c.get("percentage_contribution", 0.0),
                "direction": c.get("direction", "INCREASES_RISK"),
            }
            for c in ranked
        ],
    }


def generate_waterfall_plot(
    shap_result: Dict[str, Any],
    max_display: int = 10,
    output_path: Optional[Path] = None,
    title: Optional[str] = None,
) -> plt.Figure:
    """Generates a clean horizontal bar waterfall plot for a single instance SHAP explanation.

    Args:
        shap_result: Output from explain_activity.
        max_display: Number of top features to display.
        output_path: Optional path to save PNG figure.
        title: Optional plot title.

    Returns:
        Matplotlib Figure object.
    """
    ranked = shap_result.get("ranked_contributions", [])[:max_display]
    if not ranked:
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.text(
            0.5,
            0.5,
            "No SHAP feature contributions available",
            ha="center",
            va="center",
        )
        return fig

    # Reverse order so largest is on top
    items = list(reversed(ranked))
    names = [item["feature_name"] for item in items]
    values = [item["shap_value"] for item in items]
    colors = ["#d9534f" if v > 0 else "#5cb85c" for v in values]

    fig, ax = plt.subplots(figsize=(10, max(4, len(items) * 0.45)))
    y_pos = np.arange(len(names))

    ax.barh(y_pos, values, color=colors, align="center", edgecolor="none", height=0.65)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=9)
    ax.axvline(0, color="#333333", linestyle="--", linewidth=0.8, alpha=0.7)

    ax.set_xlabel(
        "SHAP Value (Contribution to Anomaly Reconstruction Error)", fontsize=10
    )
    ax.set_title(
        title
        or f"AIRS SHAP Feature Attribution (Anomaly Score: {shap_result.get('sai_score', 0.0):.3f})",
        fontsize=11,
        fontweight="bold",
    )
    ax.grid(axis="x", linestyle=":", alpha=0.6)
    plt.tight_layout()

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=300, bbox_inches="tight")

    return fig


def generate_summary_plot(
    shap_values_matrix: np.ndarray,
    feature_matrix: np.ndarray,
    feature_names: List[str],
    max_display: int = 15,
    output_path: Optional[Path] = None,
    plot_type: str = "bar",
) -> plt.Figure:
    """Generates global dataset SHAP summary plot (bar or beeswarm).

    Args:
        shap_values_matrix: 2D array of SHAP values of shape (N_samples, N_features).
        feature_matrix: 2D array of feature values of shape (N_samples, N_features).
        feature_names: List of human-readable or raw feature names.
        max_display: Number of top features to include in summary.
        output_path: Optional path to save PNG figure.
        plot_type: "bar" for mean absolute importance or "dot" for beeswarm.

    Returns:
        Matplotlib Figure object.
    """
    fig = plt.figure(figsize=(10, max(5, max_display * 0.4)))
    shap.summary_plot(
        shap_values_matrix,
        features=feature_matrix,
        feature_names=feature_names,
        max_display=max_display,
        plot_type=plot_type,
        show=False,
    )
    plt.title(
        "Global AIRS Anomaly Feature Importance (SHAP Summary)",
        fontsize=11,
        fontweight="bold",
    )
    plt.tight_layout()

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches="tight")

    return fig
