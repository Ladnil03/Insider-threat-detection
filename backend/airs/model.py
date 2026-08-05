"""AIRS PyTorch Autoencoder Neural Network Architecture."""

import torch
import torch.nn as nn


class AIRSAutoencoder(nn.Module):
    """PyTorch Autoencoder model for user behavior anomaly detection.

    Encodes input user feature vectors into a compressed latent representation
    and reconstructs them. Anomaly score is derived from MSE reconstruction error.
    """

    def __init__(self, input_dim: int = 16, latent_dim: int = 2) -> None:
        """Initializes encoder and decoder network layers.

        Args:
            input_dim: Number of input features.
            latent_dim: Bottleneck latent dimension size.
        """
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 8),
            nn.ReLU(),
            nn.Linear(8, latent_dim),
            nn.ReLU(),
        )
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 8),
            nn.ReLU(),
            nn.Linear(8, input_dim),
            nn.Sigmoid(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through encoder and decoder.

        Args:
            x: Input feature tensor of shape (batch_size, input_dim).

        Returns:
            Reconstructed feature tensor of shape (batch_size, input_dim).
        """
        latent = self.encoder(x)
        reconstructed = self.decoder(latent)
        return reconstructed
