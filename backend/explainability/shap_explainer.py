"""SHAP Feature Attribution Explainer for AIRS Autoencoder Reconstruction Error.

Novel Contribution & Explainer Choice Rationale:
The original research paper (Koli et al., 2025) leaves explainability as unaddressed future work.
We wrap SHAP around the autoencoder's reconstruction error to provide local feature attributions
for every flagged user anomaly.

Why KernelExplainer over DeepExplainer:
- DeepExplainer requires linear gradient backpropagation tailored for classification logits.
- The AIRS anomaly score is a non-linear composite scalar function:
    f(x) = (1 / D) * || x_scaled - Autoencoder(x_scaled) ||^2
- KernelExplainer treats f(x) as a black-box scoring function and uses weighted linear regression
  on perturbed feature coalitions to estimate exact cooperative game-theoretic Shapley values (phi_i).
- We initialize KernelExplainer with a representative background dataset of benign activity,
  guaranteeing mathematically sound and stable attribution values.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd
import shap
import torch

from airs.inference import (
    load_airs_inference_artifacts,
    normalize_reconstruction_error,
)
from airs.model import AIRSAutoencoder
from data_pipeline.config import ALL_FEATURE_COLS, PROCESSED_DATA_DIR

SCORED_PARQUET_PATH = PROCESSED_DATA_DIR / "prism_scored_activity.parquet"

# Human-Readable Feature Display Names for all base, rolling, and baseline deviation metrics
FEATURE_NAME_MAPPINGS: Dict[str, str] = {
    # 12 Base Daily Activity Features
    "logon_count": "Total Daily Logons",
    "logon_after_hours": "Off-Hours Logons (Night/Weekend)",
    "file_count": "File System Operations",
    "file_copy_usb": "USB Removable Media File Transfers",
    "file_sensitive_access": "Sensitive File Access (.exe/.zip/.iso)",
    "device_connect_count": "USB Hardware Device Connects",
    "device_disconnect_count": "USB Hardware Disconnects",
    "email_count": "Total Emails Sent",
    "email_external_count": "External Emails to Non-Corporate Domains",
    "email_large_attachment_count": "Large Email Attachments (>5MB)",
    "web_visit_count": "Total Web Browsing Requests",
    "web_job_search_count": "Job Search Board Visits",
    # 7-Day Rolling Statistics
    "logon_count_7d_mean": "Logon Volume (7-Day Avg)",
    "logon_after_hours_7d_mean": "Off-Hours Logons (7-Day Avg)",
    "file_count_7d_mean": "File Ops (7-Day Avg)",
    "file_copy_usb_7d_mean": "USB File Transfers (7-Day Avg)",
    "file_sensitive_access_7d_mean": "Sensitive Access (7-Day Avg)",
    "device_connect_count_7d_mean": "USB Connects (7-Day Avg)",
    "email_external_count_7d_mean": "External Emails (7-Day Avg)",
    "email_large_attachment_count_7d_mean": "Large Attachments (7-Day Avg)",
    "web_job_search_count_7d_mean": "Job Searches (7-Day Avg)",
    # 30-Day Baseline Deviation Z-Scores (Acute behavioral departure from trailing history)
    "logon_after_hours_baseline_dev": "Unusual Off-Hours Logon Surge (30-Day Z-Score)",
    "file_copy_usb_baseline_dev": "Mass USB File Exfiltration Spike (30-Day Z-Score)",
    "file_sensitive_access_baseline_dev": "Sensitive Archive Access Surge (30-Day Z-Score)",
    "device_connect_count_baseline_dev": "Unusual USB Hardware Usage (30-Day Z-Score)",
    "email_external_count_baseline_dev": "External Email Outflow Surge (30-Day Z-Score)",
    "email_large_attachment_count_baseline_dev": "Mass Data Attachment Spike (30-Day Z-Score)",
    "web_job_search_count_baseline_dev": "Flight Risk Job Hunting Spike (30-Day Z-Score)",
}


def get_human_readable_feature_name(feature_key: str) -> str:
    """Returns clean human-readable name for any feature column key."""
    if feature_key in FEATURE_NAME_MAPPINGS:
        return FEATURE_NAME_MAPPINGS[feature_key]

    # Clean formatting fallback for rolling/std features
    cleaned = feature_key.replace("_", " ").title()
    if "7D Mean" in cleaned:
        cleaned = cleaned.replace("7D Mean", "(7-Day Mean)")
    elif "7D Std" in cleaned:
        cleaned = cleaned.replace("7D Std", "(7-Day Volatility)")
    elif "30D Mean" in cleaned:
        cleaned = cleaned.replace("30D Mean", "(30-Day Baseline)")
    elif "30D Std" in cleaned:
        cleaned = cleaned.replace("30D Std", "(30-Day Volatility)")
    elif "Baseline Dev" in cleaned:
        cleaned = cleaned.replace("Baseline Dev", "(Baseline Z-Score)")
    return cleaned


class AIRSShapExplainer:
    """SHAP Explainer wrapping the AIRS Autoencoder model's reconstruction error."""

    def __init__(
        self,
        model: Optional[AIRSAutoencoder] = None,
        scaler: Optional[Any] = None,
        background_data: Optional[np.ndarray] = None,
        model_path: Optional[Path] = None,
        scaler_path: Optional[Path] = None,
        background_samples: int = 50,
    ) -> None:
        """Initializes KernelExplainer on autoencoder reconstruction loss.

        Args:
            model: Trained AIRSAutoencoder instance.
            scaler: Fitted StandardScaler instance.
            background_data: Array of benign background samples (unscaled).
            model_path: Path to model checkpoint.
            scaler_path: Path to scaler artifact.
            background_samples: Number of background baseline samples to sample.
        """
        if model is None or scaler is None:
            self.model, self.scaler = load_airs_inference_artifacts(
                model_path, scaler_path
            )
        else:
            self.model = model
            self.scaler = scaler

        self.model.eval()

        # Load or generate representative benign background dataset
        if background_data is None:
            background_data = self._load_default_background(
                num_samples=background_samples
            )
        self.background_unscaled = background_data

        # Define black-box scoring function f: X_unscaled -> MSE reconstruction error
        def reconstruction_error_predict_fn(x_unscaled_batch: np.ndarray) -> np.ndarray:
            x_arr = np.asarray(x_unscaled_batch, dtype=np.float32)
            if x_arr.ndim == 1:
                x_arr = x_arr.reshape(1, -1)
            x_scaled = self.scaler.transform(x_arr)
            t_input = torch.tensor(x_scaled, dtype=torch.float32)
            with torch.no_grad():
                t_rec = self.model(t_input)
                mse_errors = torch.mean((t_rec - t_input) ** 2, dim=1).numpy()
            return mse_errors

        self.predict_fn = reconstruction_error_predict_fn

        # Summarize background dataset using shap.kmeans for computational efficiency
        if len(self.background_unscaled) > background_samples:
            bg_subset = shap.kmeans(
                self.background_unscaled, min(background_samples, 25)
            )
        else:
            bg_subset = self.background_unscaled

        self.explainer = shap.KernelExplainer(
            self.predict_fn, bg_subset, link="identity"
        )
        self.expected_value = float(np.atleast_1d(self.explainer.expected_value)[0])

    def _load_default_background(self, num_samples: int = 50) -> np.ndarray:
        """Loads benign baseline activity samples from dataset or creates synthetic baseline."""
        if SCORED_PARQUET_PATH.exists():
            df = pd.read_parquet(SCORED_PARQUET_PATH)
            benign_df = (
                df[df["is_malicious"] == 0] if "is_malicious" in df.columns else df
            )
            feature_cols = [c for c in ALL_FEATURE_COLS if c in benign_df.columns]
            sample_df = benign_df[feature_cols].sample(
                n=min(num_samples, len(benign_df)), random_state=42
            )
            return sample_df.values.astype(np.float32)

        # Fallback synthetic neutral baseline
        return np.zeros((num_samples, len(ALL_FEATURE_COLS)), dtype=np.float32)

    def explain_activity(
        self,
        activity_record: Union[pd.Series, pd.DataFrame, np.ndarray, Dict[str, float]],
        top_k: int = 5,
        nsamples: int = 150,
    ) -> Dict[str, Any]:
        """Computes SHAP feature attribution breakdown for a single user activity record.

        Args:
            activity_record: Daily activity metrics (Series, DataFrame row, array, or dict).
            top_k: Number of top contributing features to highlight in summary.
            nsamples: Number of Monte Carlo coalition evaluations for KernelExplainer.

        Returns:
            Dictionary containing base_value, reconstruction_error, sai_score, ranked_contributions,
            and human_readable_summary.
        """
        # Convert input to 1D float array and feature names
        if isinstance(activity_record, dict):
            feat_names = [c for c in ALL_FEATURE_COLS if c in activity_record]
            feat_values = np.array(
                [activity_record.get(c, 0.0) for c in feat_names], dtype=np.float32
            )
        elif isinstance(activity_record, pd.Series):
            feat_names = [c for c in ALL_FEATURE_COLS if c in activity_record.index]
            feat_values = activity_record[feat_names].values.astype(np.float32)
        elif isinstance(activity_record, pd.DataFrame):
            feat_names = [c for c in ALL_FEATURE_COLS if c in activity_record.columns]
            feat_values = activity_record[feat_names].iloc[0].values.astype(np.float32)
        else:
            feat_values = np.asarray(activity_record, dtype=np.float32).ravel()
            feat_names = ALL_FEATURE_COLS[: len(feat_values)]

        # Calculate actual MSE reconstruction error and normalized SAI score
        mse_error = float(self.predict_fn(feat_values.reshape(1, -1))[0])
        sai_score = float(normalize_reconstruction_error(mse_error))

        # Compute Shapley values
        shap_values_raw = self.explainer.shap_values(
            feat_values.reshape(1, -1), nsamples=nsamples
        )
        shap_values = np.asarray(shap_values_raw).ravel()

        # Compute percentage contribution of positive risk-elevating features
        pos_shap_sum = float(np.sum(np.maximum(0.0, shap_values)))
        if pos_shap_sum <= 0.0:
            pos_shap_sum = float(np.sum(np.abs(shap_values))) or 1.0

        contributions: List[Dict[str, Any]] = []
        for name, val, phi in zip(feat_names, feat_values, shap_values):
            pct = (
                max(0.0, float(phi)) / pos_shap_sum * 100.0 if pos_shap_sum > 0 else 0.0
            )
            contributions.append(
                {
                    "feature_key": name,
                    "feature_name": get_human_readable_feature_name(name),
                    "feature_value": float(val),
                    "shap_value": round(float(phi), 4),
                    "percentage_contribution": round(pct, 1),
                    "direction": "INCREASES_RISK" if phi > 0 else "DECREASES_RISK",
                }
            )

        # Sort contributions by absolute magnitude
        contributions_sorted = sorted(
            contributions, key=lambda x: abs(x["shap_value"]), reverse=True
        )
        top_risk_drivers = [
            c for c in contributions_sorted if c["direction"] == "INCREASES_RISK"
        ][:top_k]

        # Generate plain-English explanation summary
        if top_risk_drivers:
            summary_clauses = [
                f"{c['feature_name']}: {c['percentage_contribution']:.1f}%"
                for c in top_risk_drivers
                if c["percentage_contribution"] > 1.0
            ]
            if summary_clauses:
                summary_text = "Primary risk drivers: " + ", ".join(summary_clauses)
            else:
                summary_text = "Activity aligns closely with baseline profile; minimal anomalous deviations detected."
        else:
            summary_text = "Activity profile matches normal benign baseline."

        return {
            "base_value": round(self.expected_value, 4),
            "reconstruction_error": round(mse_error, 4),
            "sai_score": round(sai_score, 4),
            "ranked_contributions": contributions_sorted,
            "top_risk_drivers": top_risk_drivers,
            "human_readable_summary": summary_text,
            "all_shap_values": shap_values.tolist(),
            "feature_names": feat_names,
        }
