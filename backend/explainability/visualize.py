"""Visualization Helpers for SHAP Summary and Attribution Data."""

from typing import Any, Dict


def format_shap_summary_dict(shap_result: Dict[str, Any]) -> Dict[str, Any]:
    """Formats raw SHAP output into a clean JSON-serializable structure for frontend Recharts rendering.

    Args:
        shap_result: Output from compute_shap_explanations.

    Returns:
        Structured chart payload with sorted feature importances.
    """
    attributions = shap_result.get("feature_attributions", {})
    sorted_features = sorted(
        [{"feature": k, "attribution": v} for k, v in attributions.items()],
        key=lambda x: abs(x["attribution"]),
        reverse=True,
    )
    return {
        "base_value": shap_result.get("base_value", 0.0),
        "features": sorted_features,
    }
