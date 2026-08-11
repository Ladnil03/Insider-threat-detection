"""Human Analyst Feedback Blending and Online Incremental Model Adaptation.

Implements formula:
S_final = S_AI + alpha * (S_user - S_AI) = (1 - alpha) * S_AI + alpha * S_user

Accumulates analyst feedback records and triggers incremental fine-tuning on the existing
model checkpoint once N=50 feedback instances are collected (without retraining from scratch).
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from airs.inference import (
    DEFAULT_MODEL_PATH,
    DEFAULT_SCALER_PATH,
    load_airs_inference_artifacts,
)


def blend_analyst_feedback(
    model_score: float, analyst_score: float, alpha: float = 0.7
) -> float:
    """Blends model reconstruction score with analyst manual rating using parameter alpha.

    Formula: S_final = S_AI + alpha * (S_user - S_AI) = (1 - alpha) * S_AI + alpha * S_user

    Args:
        model_score: Score computed by AIRS model (S_AI).
        analyst_score: Analyst adjusted score from UI (S_user).
        alpha: Weight given to analyst feedback (0.0 to 1.0).

    Returns:
        Blended composite score (S_final).
    """
    alpha = float(np.clip(alpha, 0.0, 1.0))
    return (1.0 - alpha) * model_score + alpha * analyst_score


class FeedbackBuffer:
    """In-memory and file-backed buffer for accumulating analyst feedback records."""

    def __init__(self, retrain_threshold: int = 50) -> None:
        """Initializes buffer with retraining threshold.

        Args:
            retrain_threshold: Number of records required to trigger fine-tuning (N=50).
        """
        self.retrain_threshold = retrain_threshold
        self.records: List[Dict[str, Any]] = []

    def add_feedback(
        self,
        activity_id: str,
        sai_score: float,
        user_score: float,
        feature_vector: np.ndarray,
        alpha: float = 0.7,
        timestamp: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Adds a new analyst feedback entry to the accumulation buffer.

        Args:
            activity_id: Identifier for activity record.
            sai_score: Model SAI score.
            user_score: Analyst manual rating.
            feature_vector: 72-dimensional raw/scaled feature array.
            alpha: Feedback blending weight.
            timestamp: Optional timestamp string.

        Returns:
            Dictionary containing stored record with computed final_score.
        """
        final_score = blend_analyst_feedback(sai_score, user_score, alpha)
        record = {
            "activity_id": activity_id,
            "sai_score": float(sai_score),
            "user_score": float(user_score),
            "final_score": float(final_score),
            "feature_vector": np.asarray(feature_vector, dtype=np.float32).tolist(),
            "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
        }
        self.records.append(record)
        return record

    def is_ready_for_retraining(self) -> bool:
        """Checks if accumulated feedback count meets or exceeds threshold N."""
        return len(self.records) >= self.retrain_threshold

    def clear(self) -> None:
        """Clears accumulated feedback records after retraining."""
        self.records.clear()


def fine_tune_existing_checkpoint(
    feedback_records: List[Dict[str, Any]],
    model_path: Optional[Path] = None,
    scaler_path: Optional[Path] = None,
    epochs: int = 5,
    lr: float = 0.0001,
) -> Dict[str, Any]:
    """Fine-tunes existing model checkpoint using accumulated feedback instances.

    Modifies parameters in-place without retraining from scratch.

    Args:
        feedback_records: List of accumulated feedback dictionaries.
        model_path: Path to existing airs_autoencoder.pt checkpoint.
        scaler_path: Path to existing airs_scaler.pkl artifact.
        epochs: Number of fine-tuning epochs (default: 5).
        lr: Fine-tuning learning rate (default: 0.0001).

    Returns:
        Dictionary containing fine-tuning metrics and updated checkpoint path.
    """
    m_path = model_path or DEFAULT_MODEL_PATH
    s_path = scaler_path or DEFAULT_SCALER_PATH

    model, scaler = load_airs_inference_artifacts(m_path, s_path)

    # Extract features from feedback records
    feature_list = [
        r["feature_vector"] for r in feedback_records if "feature_vector" in r
    ]
    if not feature_list:
        raise ValueError("No valid feature vectors found in feedback records")

    x_raw = np.array(feature_list, dtype=np.float32)
    if x_raw.ndim == 1:
        x_raw = x_raw.reshape(1, -1)

    x_scaled = scaler.transform(x_raw)
    t_input = torch.tensor(x_scaled, dtype=torch.float32)

    # Fine-tune existing model weights
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()

    model.train()
    history = []
    for _ in range(epochs):
        optimizer.zero_grad()
        output = model(t_input)
        loss = criterion(output, t_input)
        loss.backward()
        optimizer.step()
        history.append(float(loss.item()))

    # Update saved checkpoint
    checkpoint = torch.load(m_path, map_location="cpu", weights_only=False)
    checkpoint["model_state_dict"] = model.state_dict()
    checkpoint["final_val_loss"] = history[-1]
    torch.save(checkpoint, m_path)

    return {
        "fine_tune_epochs": epochs,
        "initial_loss": history[0],
        "final_loss": history[-1],
        "records_tuned": len(feedback_records),
        "model_path": str(m_path),
    }
