# AIRS — Adaptive Insider Risk Scoring (Autoencoder)

PyTorch autoencoder trained on benign activity. Scores new activity by reconstruction error — higher error = higher risk. Supports human-feedback blending and periodic retraining.

**Inputs:** Normalized feature vectors
**Outputs:** Risk score [0–1] per activity window
