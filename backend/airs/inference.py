"""Inference / scoring with the trained AIRS autoencoder.

Computes reconstruction error for new activity and maps it to a risk
score in [0, 1] via percentile-based normalisation.
"""


def score_activity(features) -> float:
    """Compute AIRS risk score for a single activity feature vector.

    Args:
        features: numpy array or torch Tensor of shape (input_dim,).

    Returns:
        Risk score in [0, 1].

    Todo:
        Implement reconstruction error → risk score mapping in Week 4.

    """
    raise NotImplementedError("Week 4 — implement scoring logic.")
