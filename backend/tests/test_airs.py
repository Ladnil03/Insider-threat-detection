"""Unit and Integration Tests for AIRS Autoencoder Architecture, Inference, Feedback, and Ensemble Scoring."""

import math
import tempfile
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import StandardScaler

from airs.ensemble import compute_ensemble_score
from airs.feedback import (
    FeedbackBuffer,
    blend_analyst_feedback,
    fine_tune_existing_checkpoint,
)
from airs.inference import (
    compute_reconstruction_risk,
    normalize_reconstruction_error,
    score_activity_features,
)
from airs.model import AIRSAutoencoder


def test_airs_autoencoder_shape_default_72() -> None:
    """Tests that default AIRS autoencoder produces matching (batch_size, 72) output shape."""
    model = AIRSAutoencoder(input_dim=72, hidden_dims=[48, 24], latent_dim=12)
    sample_input = torch.randn(8, 72)
    output = model(sample_input)
    assert output.shape == (8, 72)

    latent = model.encode(sample_input)
    assert latent.shape == (8, 12)


def test_airs_training_loss_decreases_on_minibatch() -> None:
    """Tests that PyTorch training loss decreases over epochs on a mini-batch."""
    torch.manual_seed(42)
    model = AIRSAutoencoder(input_dim=72, hidden_dims=[48, 24], latent_dim=12)
    optimizer = optim.Adam(model.parameters(), lr=0.01)
    criterion = nn.MSELoss()

    batch_x = torch.randn(32, 72)

    model.train()
    optimizer.zero_grad()
    initial_output = model(batch_x)
    initial_loss = criterion(initial_output, batch_x).item()

    for _ in range(15):
        optimizer.zero_grad()
        out = model(batch_x)
        loss = criterion(out, batch_x)
        loss.backward()
        optimizer.step()

    final_loss = loss.item()
    assert (
        final_loss < initial_loss
    ), f"Loss should decrease: initial={initial_loss:.4f}, final={final_loss:.4f}"


def test_normalize_reconstruction_error() -> None:
    """Tests reconstruction error scaling to [0.0, 1.0] SAI anomaly score."""
    assert math.isclose(
        normalize_reconstruction_error(0.05, min_ref=0.05, max_ref=2.50), 0.0
    )
    assert math.isclose(
        normalize_reconstruction_error(2.50, min_ref=0.05, max_ref=2.50), 1.0
    )
    assert math.isclose(
        normalize_reconstruction_error(1.275, min_ref=0.05, max_ref=2.50), 0.5
    )

    arr = np.array([0.05, 1.275, 2.50])
    norm_arr = normalize_reconstruction_error(arr, min_ref=0.05, max_ref=2.50)
    np.testing.assert_array_almost_equal(norm_arr, np.array([0.0, 0.5, 1.0]))


def test_compute_reconstruction_risk_scalar() -> None:
    """Tests reconstruction risk calculation on single sample tensor."""
    model = AIRSAutoencoder(input_dim=72)
    sample = torch.randn(1, 72)
    risk = compute_reconstruction_risk(model, sample)
    assert isinstance(risk, float)
    assert risk >= 0.0


def test_score_activity_features_with_sai() -> None:
    """Tests end-to-end scoring pipeline with mock scaler and model returning SAI score."""
    model = AIRSAutoencoder(input_dim=72)
    scaler = StandardScaler()
    synthetic_data = np.random.randn(10, 72)
    scaler.fit(synthetic_data)

    single_sample = synthetic_data[0]
    res = score_activity_features(single_sample, model=model, scaler=scaler)

    assert "mse_reconstruction_error" in res
    assert "sai_score" in res
    assert 0.0 <= res["sai_score"] <= 1.0


def test_ensemble_score_weighted_combination() -> None:
    """Tests weighted ensemble score combination formula S_ensemble = beta*S_PRISM + (1-beta)*SAI."""
    prism_score = 0.8
    sai_score = 0.4

    # Equal weights (beta = 0.5)
    ens_05 = compute_ensemble_score(prism_score, sai_score, beta=0.5)
    assert round(ens_05, 4) == 0.60

    # Heavily PRISM weighted (beta = 0.75)
    ens_075 = compute_ensemble_score(prism_score, sai_score, beta=0.75)
    assert round(ens_075, 4) == 0.70

    # Vectorized array ensemble scoring
    arr_p = np.array([0.0, 0.5, 1.0])
    arr_s = np.array([1.0, 0.5, 0.0])
    arr_ens = compute_ensemble_score(arr_p, arr_s, beta=0.5)
    np.testing.assert_array_almost_equal(arr_ens, np.array([0.5, 0.5, 0.5]))


def test_blend_analyst_feedback() -> None:
    """Tests analyst feedback blending math: S_final = (1-a)*S_AI + a*S_user."""
    blended = blend_analyst_feedback(model_score=0.2, analyst_score=0.8, alpha=0.7)
    assert round(blended, 4) == 0.62


def test_feedback_buffer_accumulation() -> None:
    """Tests analyst feedback buffer accumulation and threshold readiness trigger."""
    buffer = FeedbackBuffer(retrain_threshold=3)
    assert not buffer.is_ready_for_retraining()

    feat = np.zeros(72)
    buffer.add_feedback("ACT-001", sai_score=0.3, user_score=0.9, feature_vector=feat)
    buffer.add_feedback("ACT-002", sai_score=0.4, user_score=0.8, feature_vector=feat)
    assert not buffer.is_ready_for_retraining()

    buffer.add_feedback("ACT-003", sai_score=0.2, user_score=0.9, feature_vector=feat)
    assert buffer.is_ready_for_retraining()
    assert len(buffer.records) == 3

    buffer.clear()
    assert len(buffer.records) == 0


def test_fine_tune_existing_checkpoint_mock() -> None:
    """Tests fine-tuning checkpoint state dict using synthetic feedback records."""
    model = AIRSAutoencoder(input_dim=72)
    scaler = StandardScaler()
    synthetic_data = np.random.randn(10, 72).astype(np.float32)
    scaler.fit(synthetic_data)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        m_file = tmp_path / "airs_autoencoder.pt"
        s_file = tmp_path / "airs_scaler.pkl"

        import joblib

        torch.save(
            {
                "model_state_dict": model.state_dict(),
                "config": {"model": {"input_dim": 72}},
            },
            m_file,
        )
        joblib.dump(scaler, s_file)

        records = [
            {"activity_id": f"ACT-{i}", "feature_vector": synthetic_data[i].tolist()}
            for i in range(5)
        ]

        res = fine_tune_existing_checkpoint(
            records, model_path=m_file, scaler_path=s_file, epochs=3, lr=0.0001
        )

        assert res["records_tuned"] == 5
        assert res["fine_tune_epochs"] == 3
        assert res["final_loss"] <= res["initial_loss"] + 0.1
