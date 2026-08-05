# AIRS Autoencoder Module

AIRS (Adaptive Insider Risk Scoring) is a PyTorch-based Autoencoder model trained on benign user behavior patterns.

## Purpose
- Detects subtle behavioral anomalies by measuring reconstruction error.
- Blends analyst feedback into composite risk ratings.
- Retrains periodically when new analyst feedback thresholds are reached.

## Inputs
- Scaled daily user activity feature vectors.

## Outputs
- Anomaly reconstruction loss score [0.0, 1.0].
