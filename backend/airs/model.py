"""AIRS (Adaptive Insider Risk System) PyTorch Autoencoder Neural Network Architecture.

Input Dimensionality Justification:
The input feature vector dimension is D_in = 72 (12 daily base activity metrics +
48 7-day and 30-day rolling mean/std statistics + 12 30-day standardized baseline z-scores).

Symmetric Layer Compression Rationale:
- Input (72) -> Hidden Layer 1 (48): First compression step filters redundant correlation between base metrics and rolling averages (1.5x reduction).
- Hidden Layer 1 (48) -> Hidden Layer 2 (24): Second compression step condenses temporal statistics into high-level behavioral patterns (2.0x reduction).
- Hidden Layer 2 (24) -> Bottleneck Latent Space (12): Compresses full activity matrix to a 12-dimensional bottleneck representation (6:1 total compression ratio).
  Forces the autoencoder to learn compact, noise-free latent representations of benign behavior profiles.
- Decoder mirror: Reconstructs 12 -> 24 -> 48 -> 72 features. Reconstruction error (MSE) measures deviation from benign baseline.
"""

from typing import List, Optional

import torch
import torch.nn as nn


class AIRSAutoencoder(nn.Module):
    """PyTorch Autoencoder model for user behavior anomaly detection.

    Encodes input user feature vectors into a compressed latent representation
    and reconstructs them. Anomaly score is derived from MSE reconstruction error:
    L_MSE(x, x_hat) = (1 / D) * sum_{i=1}^D (x_i - x_hat_i)^2
    """

    def __init__(
        self,
        input_dim: int = 72,
        hidden_dims: Optional[List[int]] = None,
        latent_dim: int = 12,
        dropout_rate: float = 0.1,
    ) -> None:
        """Initializes symmetric encoder and decoder network layers.

        Args:
            input_dim: Number of input features (default: 72).
            hidden_dims: Intermediate encoder layer dimensions (default: [48, 24]).
            latent_dim: Bottleneck latent dimension size (default: 12).
            dropout_rate: Dropout probability for regularizing hidden layers.
        """
        super().__init__()
        self.input_dim = input_dim
        self.latent_dim = latent_dim
        hidden_dims = hidden_dims or [48, 24]

        # 1. Build Encoder (72 -> 48 -> 24 -> 12)
        encoder_layers: List[nn.Module] = []
        prev_dim = input_dim
        for h_dim in hidden_dims:
            encoder_layers.append(nn.Linear(prev_dim, h_dim))
            encoder_layers.append(nn.LeakyReLU(negative_slope=0.1))
            if dropout_rate > 0.0:
                encoder_layers.append(nn.Dropout(p=dropout_rate))
            prev_dim = h_dim

        encoder_layers.append(nn.Linear(prev_dim, latent_dim))
        encoder_layers.append(nn.LeakyReLU(negative_slope=0.1))
        self.encoder = nn.Sequential(*encoder_layers)

        # 2. Build Symmetric Decoder (12 -> 24 -> 48 -> 72)
        decoder_layers: List[nn.Module] = []
        prev_dim = latent_dim
        for h_dim in reversed(hidden_dims):
            decoder_layers.append(nn.Linear(prev_dim, h_dim))
            decoder_layers.append(nn.LeakyReLU(negative_slope=0.1))
            if dropout_rate > 0.0:
                decoder_layers.append(nn.Dropout(p=dropout_rate))
            prev_dim = h_dim

        decoder_layers.append(nn.Linear(prev_dim, input_dim))
        # Linear activation on output layer to support standardized z-scores
        self.decoder = nn.Sequential(*decoder_layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass executing encoder bottleneck compression and decoder reconstruction.

        Args:
            x: Input feature tensor of shape (batch_size, input_dim).

        Returns:
            Reconstructed feature tensor of shape (batch_size, input_dim).
        """
        latent = self.encoder(x)
        reconstructed = self.decoder(latent)
        return reconstructed

    def encode(self, x: torch.Tensor) -> torch.Tensor:
        """Helper method to extract the 12-dimensional bottleneck latent embedding.

        Args:
            x: Input feature tensor of shape (batch_size, input_dim).

        Returns:
            Latent representation tensor of shape (batch_size, latent_dim).
        """
        return self.encoder(x)
