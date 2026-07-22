"""PyTorch autoencoder architecture for AIRS.

Learns a compressed representation of benign user activity; high
reconstruction error on new activity indicates anomalous (risky)
behaviour.
"""

import torch.nn as nn


class Autoencoder(nn.Module):
    """Feedforward autoencoder with configurable hidden layers."""

    def __init__(
        self,
        input_dim: int,
        encoding_dim: int,
        hidden_dims: list[int],
        dropout: float = 0.1,
    ) -> None:
        """Initialise encoder-decoder architecture.

        Args:
            input_dim: Number of input features.
            encoding_dim: Bottleneck layer size.
            hidden_dims: Sizes of hidden layers in the encoder.
            dropout: Dropout probability between layers.

        """
        super().__init__()
        # ponytail: one linear stack — keep it simple;
        #   deeper architectures if validation loss plateaus.
        layers: list[nn.Module] = []
        prev = input_dim
        for h in hidden_dims:
            layers.extend([nn.Linear(prev, h), nn.ReLU(), nn.Dropout(dropout)])
            prev = h
        layers.append(nn.Linear(prev, encoding_dim))
        self.encoder = nn.Sequential(*layers)

        decoder_dims = list(reversed(hidden_dims))
        dec_layers: list[nn.Module] = []
        prev = encoding_dim
        for h in decoder_dims:
            dec_layers.extend([nn.Linear(prev, h), nn.ReLU(), nn.Dropout(dropout)])
            prev = h
        dec_layers.append(nn.Linear(prev, input_dim))
        self.decoder = nn.Sequential(*dec_layers)

    def forward(self, x):
        """Forward pass: encode then decode."""
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded
