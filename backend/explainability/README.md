# Explainability

SHAP-based feature attribution on the AIRS autoencoder risk score. Produces per-feature contribution values and summary/force plots.

**Inputs:** AIRS model + activity feature vector
**Outputs:** SHAP values (dict of feature → contribution) + optional plots
