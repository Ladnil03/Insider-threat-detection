"""AIRS Anomaly Risk Scoring Inference Module.

Loads trained model state dict and fitted StandardScaler to compute MSE reconstruction error
and normalized SAI anomaly risk scores [0.0, 1.0] on daily user activity feature vectors.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

import joblib
import numpy as np
import pandas as pd
import torch

from airs.model import AIRSAutoencoder
from data_pipeline.config import BASE_BACKEND_DIR

DEFAULT_CHECKPOINT_DIR = BASE_BACKEND_DIR / "checkpoints"
DEFAULT_MODEL_PATH = DEFAULT_CHECKPOINT_DIR / "airs_autoencoder.pt"
DEFAULT_SCALER_PATH = DEFAULT_CHECKPOINT_DIR / "airs_scaler.pkl"


def load_airs_inference_artifacts(
    model_path: Optional[Path] = None,
    scaler_path: Optional[Path] = None,
) -> Tuple[AIRSAutoencoder, Any]:
    """Loads trained AIRSAutoencoder model and fitted StandardScaler.

    Args:
        model_path: Path to airs_autoencoder.pt checkpoint file.
        scaler_path: Path to airs_scaler.pkl artifact file.

    Returns:
        Tuple of (initialized_eval_model, fitted_scaler).
    """
    m_path = model_path or DEFAULT_MODEL_PATH
    s_path = scaler_path or DEFAULT_SCALER_PATH

    if not m_path.exists():
        raise FileNotFoundError(f"AIRS model checkpoint not found at {m_path}")
    if not s_path.exists():
        raise FileNotFoundError(f"AIRS scaler artifact not found at {s_path}")

    checkpoint = torch.load(m_path, map_location="cpu", weights_only=False)
    cfg = checkpoint.get("config", {}).get("model", {})

    model = AIRSAutoencoder(
        input_dim=cfg.get("input_dim", 72),
        hidden_dims=cfg.get("hidden_dims", [48, 24]),
        latent_dim=cfg.get("latent_dim", 12),
        dropout_rate=cfg.get("dropout_rate", 0.1),
    )
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    scaler = joblib.load(s_path)
    return model, scaler


def normalize_reconstruction_error(
    errors: Union[float, np.ndarray, pd.Series],
    min_ref: float = 0.05,
    max_ref: float = 2.50,
) -> Union[float, np.ndarray, pd.Series]:
    """Normalizes raw MSE reconstruction error into [0.0, 1.0] SAI anomaly score.

    Formula: SAI = clip((MSE - min_ref) / (max_ref - min_ref), 0.0, 1.0)

    Args:
        errors: Raw MSE reconstruction error scalar, numpy array, or pandas Series.
        min_ref: Reference minimum baseline reconstruction error.
        max_ref: Reference maximum reconstruction error threshold.

    Returns:
        Normalized SAI anomaly score(s) strictly bounded between 0.0 and 1.0.
    """
    if max_ref == min_ref:
        if isinstance(errors, (np.ndarray, pd.Series)):
            return np.zeros_like(errors, dtype=float)
        return 0.0

    normalized = (errors - min_ref) / (max_ref - min_ref)
    if isinstance(normalized, (np.ndarray, pd.Series)):
        return np.clip(normalized, 0.0, 1.0)
    return float(np.clip(normalized, 0.0, 1.0))


def compute_reconstruction_risk(
    model: AIRSAutoencoder,
    feature_tensor: torch.Tensor,
) -> float:
    """Computes scalar MSE reconstruction error on a single user sample.

    Args:
        model: AIRSAutoencoder instance.
        feature_tensor: Single sample tensor of shape (1, input_dim) or (input_dim,).

    Returns:
        Reconstruction loss scalar value.
    """
    model.eval()
    if feature_tensor.ndim == 1:
        feature_tensor = feature_tensor.unsqueeze(0)

    with torch.no_grad():
        reconstructed = model(feature_tensor)
        loss = torch.mean((reconstructed - feature_tensor) ** 2, dim=1)
    return float(loss.item())


def score_activity_features(
    features: Union[np.ndarray, pd.DataFrame, pd.Series],
    model: Optional[AIRSAutoencoder] = None,
    scaler: Optional[Any] = None,
    model_path: Optional[Path] = None,
    scaler_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Scores unscaled raw feature vectors and returns MSE reconstruction error and SAI score.

    Args:
        features: Feature array, Series, or DataFrame (length or width 72).
        model: Optional pre-loaded model instance.
        scaler: Optional pre-loaded scaler instance.
        model_path: Path to model checkpoint if not pre-loaded.
        scaler_path: Path to scaler artifact if not pre-loaded.

    Returns:
        Dictionary containing 'mse_reconstruction_error', 'sai_score', and 'all_mse_errors'.
    """
    if model is None or scaler is None:
        model, scaler = load_airs_inference_artifacts(model_path, scaler_path)

    if isinstance(features, (pd.Series, pd.DataFrame)):
        vals = features.values
    else:
        vals = features

    if vals.ndim == 1:
        vals = vals.reshape(1, -1)

    scaled_vals = scaler.transform(vals.astype("float32"))
    t_input = torch.tensor(scaled_vals, dtype=torch.float32)

    model.eval()
    with torch.no_grad():
        t_reconstructed = model(t_input)
        mse_losses = torch.mean((t_reconstructed - t_input) ** 2, dim=1).numpy()

    sai_scores = normalize_reconstruction_error(mse_losses)

    if isinstance(sai_scores, np.ndarray):
        sai_list = sai_scores.tolist()
        single_sai = float(sai_scores[0])
    else:
        sai_list = [float(sai_scores)]
        single_sai = float(sai_scores)

    return {
        "mse_reconstruction_error": float(mse_losses[0]),
        "sai_score": single_sai,
        "all_mse_errors": mse_losses.tolist(),
        "all_sai_scores": sai_list,
    }
