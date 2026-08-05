"""Unit Tests for AIRS Autoencoder Architecture and Feedback."""

import torch

from airs.feedback import blend_analyst_feedback
from airs.model import AIRSAutoencoder


def test_airs_autoencoder_shape() -> None:
    """Tests that AIRS autoencoder outputs tensor matching input dimensions."""
    model = AIRSAutoencoder(input_dim=16, latent_dim=2)
    sample_input = torch.randn(4, 16)
    output = model(sample_input)
    assert output.shape == (4, 16)


def test_blend_analyst_feedback() -> None:
    """Tests feedback blending computation math."""
    blended = blend_analyst_feedback(model_score=0.2, analyst_score=0.8, alpha=0.7)
    assert round(blended, 4) == 0.62
