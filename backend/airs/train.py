"""Training loop for the AIRS autoencoder.

Trains on benign-activity feature vectors, validates on a held-out
split, and saves the best checkpoint.
"""


def train_autoencoder(
    train_features,
    val_features,
    config_path: str = "airs/config.yaml",
) -> float:
    """Train the autoencoder and return best validation loss.

    Args:
        train_features: numpy array or torch Tensor of benign features.
        val_features: Validation split.
        config_path: Path to AIRS config YAML.

    Returns:
        Best validation loss achieved.

    Todo:
        Implement training loop in Week 4.

    """
    raise NotImplementedError("Week 4 — implement training loop.")
