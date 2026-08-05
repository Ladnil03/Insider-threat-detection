# Explainability Module

This module provides game-theoretic feature attribution using SHAP (SHapley Additive exPlanations) for the PyTorch AIRS model.

## Novelty Contribution
While the paper leaves explainability to future work, OpenIRM adds SHAP attribution on top of the autoencoder reconstruction loss to pinpoint which exact behaviors drove the risk score.

## Inputs
- Trained AIRS autoencoder model.
- Background reference dataset.
- Target user feature sample.

## Outputs
- Quantitative feature attribution breakdown and frontend-ready visualization payloads.
