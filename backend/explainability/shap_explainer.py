"""SHAP-based explainability wrapper for the AIRS autoencoder.

Computes per-feature SHAP values (KernelExplainer or DeepExplainer)
for a given activity, attributing the autoencoder's reconstruction
error to individual input features.
"""


def explain_activity(features, model, feature_names: list[str]) -> dict:
    """Compute SHAP values for a single activity's risk score.

    Args:
        features: numpy array of shape (input_dim,).
        model: Trained AIRS Autoencoder.
        feature_names: Human-readable names for each feature.

    Returns:
        Dict mapping feature name → SHAP value.

    Todo:
        Implement SHAP computation in Week 6.

    """
    raise NotImplementedError("Week 6 — implement SHAP explainer.")
