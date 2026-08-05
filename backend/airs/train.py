"""AIRS Model Training Loop."""

from typing import Any, Dict

import torch
import torch.nn as nn
import torch.optim as optim

from airs.model import AIRSAutoencoder


def train_autoencoder(
    model: AIRSAutoencoder,
    train_loader: torch.utils.data.DataLoader,
    epochs: int = 10,
    lr: float = 0.001,
) -> Dict[str, Any]:
    """Trains the AIRS Autoencoder model on benign baseline user activity.

    Args:
        model: AIRSAutoencoder instance.
        train_loader: PyTorch DataLoader containing benign training tensors.
        epochs: Number of training epochs.
        lr: Learning rate.

    Returns:
        Dictionary containing training loss history.
    """
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()
    history = []

    model.train()
    for epoch in range(epochs):
        total_loss = 0.0
        for batch in train_loader:
            optimizer.zero_grad()
            output = model(batch)
            loss = criterion(output, batch)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        history.append(total_loss)

    return {"loss_history": history}
