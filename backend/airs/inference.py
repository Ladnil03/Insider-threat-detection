"""AIRS Anomaly Risk Scoring Inference Module."""

import torch
import torch.nn as nn

from airs.model import AIRSAutoencoder


def compute_reconstruction_risk(
    model: AIRSAutoencoder, feature_tensor: torch.Tensor
) -> float:
    """Computes anomaly risk score based on MSE reconstruction error.

    Args:
        model: Trained AIRSAutoencoder model.
        feature_tensor: Input tensor for a single user sample (1, input_dim).

    Returns:
        Scalar reconstruction loss value representing risk score.
    """
    model.eval()
    with torch.no_grad():
        reconstructed = model(feature_tensor)
        loss = nn.functional.mse_loss(reconstructed, feature_tensor)
    return float(loss.item())
