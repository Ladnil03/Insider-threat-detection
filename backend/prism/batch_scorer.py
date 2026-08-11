"""Batch scoring pipeline for PRISM rule engine.

Ingests activity_features.parquet, applies PRISM scoring formula,
and exports prism_scored_activity.parquet with labeled risk scores.
"""

from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd

from data_pipeline.config import PROCESSED_DATA_DIR, PROCESSED_PARQUET_PATH
from prism.buckets import classify_risk_score, min_max_normalize
from prism.scorer import load_prism_config, user_privilege_score

PRISM_SCORED_PARQUET_PATH = PROCESSED_DATA_DIR / "prism_scored_activity.parquet"


def score_dataframe(
    df: pd.DataFrame, custom_weights: Optional[Dict[str, float]] = None
) -> pd.DataFrame:
    """Vectorized batch scoring of user-day activity feature matrix.

    Args:
        df: DataFrame containing daily user activity features.
        custom_weights: Optional weights dictionary override.

    Returns:
        DataFrame with added 'prism_raw_score', 'prism_score', and 'prism_risk_level'.
    """
    scored_df = df.copy()
    cfg = load_prism_config()
    w = custom_weights or cfg.get("weights", {})
    t = cfg.get("thresholds", {})

    # Extract required feature columns with defaults if absent
    roles = (
        df["role"] if "role" in df.columns else pd.Series("employee", index=df.index)
    )
    file_copy_usb = (
        df["file_copy_usb"]
        if "file_copy_usb" in df.columns
        else pd.Series(0.0, index=df.index)
    )
    file_sensitive = (
        df["file_sensitive_access"]
        if "file_sensitive_access" in df.columns
        else pd.Series(0.0, index=df.index)
    )
    email_ext = (
        df["email_external_count"]
        if "email_external_count" in df.columns
        else pd.Series(0.0, index=df.index)
    )
    email_large = (
        df["email_large_attachment_count"]
        if "email_large_attachment_count" in df.columns
        else pd.Series(0.0, index=df.index)
    )
    web_job = (
        df["web_job_search_count"]
        if "web_job_search_count" in df.columns
        else pd.Series(0.0, index=df.index)
    )
    file_count = (
        df["file_count"]
        if "file_count" in df.columns
        else pd.Series(0.0, index=df.index)
    )
    logon_after = (
        df["logon_after_hours"]
        if "logon_after_hours" in df.columns
        else pd.Series(0.0, index=df.index)
    )
    device_conn = (
        df["device_connect_count"]
        if "device_connect_count" in df.columns
        else pd.Series(0.0, index=df.index)
    )

    # 1. Sp: User Privilege
    sp = roles.map(user_privilege_score).astype(float)

    # 2. SA: Activity Type Score
    sa = pd.Series(0.1, index=df.index)
    sa = np.where(file_count > 0, 0.3, sa)
    sa = np.where((web_job > 0) | (email_ext > 0) | (email_large > 0), 0.7, sa)
    sa = np.where(file_sensitive > 0, 0.8, sa)
    sa = np.where(file_copy_usb > 0, 1.0, sa)

    # 3. SC: Application Context Score
    sc = pd.Series(0.1, index=df.index)
    sc = np.where(file_sensitive > 0, 0.5, sc)
    sc = np.where(email_ext > 0, 0.6, sc)
    sc = np.where(web_job > 0, 0.7, sc)
    sc = np.where((file_copy_usb > 0) | (device_conn > 0), 0.8, sc)

    # 4. SIP: IP Address Score (off-hours indicates off-network remote access)
    sip = np.where(logon_after > 0, 0.5, 0.0)

    # 5. SB: Business Hours Score
    sb = np.where(logon_after > 0, 1.0, 0.0)

    # 6. SD: Device Compliance Score
    sd = np.where(device_conn > 0, 0.7, 0.0)

    # 7. SCA: Cumulative Activity Score
    high_risk_vol = (
        (file_copy_usb * 4.0)
        + (file_sensitive * 2.0)
        + (web_job * 2.0)
        + (email_ext * 1.5)
    )
    sca = np.clip(high_risk_vol / 10.0, 0.0, 1.0)

    # Calculate raw PRISM score
    raw_score = (
        w.get("user_privilege", 0.20) * sp
        + w.get("activity_type", 0.15) * sa
        + w.get("application_context", 0.15) * sc
        + w.get("ip_address", 0.15) * sip
        + w.get("business_hours", 0.15) * sb
        + w.get("device_compliance", 0.10) * sd
        + w.get("cumulative_activity", 0.10) * sca
    )

    norm_score = min_max_normalize(raw_score, min_val=0.0, max_val=1.0)

    scored_df["prism_raw_score"] = np.round(raw_score, 4)
    scored_df["prism_score"] = np.round(norm_score, 4)
    scored_df["prism_risk_level"] = scored_df["prism_score"].map(
        lambda s: classify_risk_score(s, t)
    )

    return scored_df


def run_batch_scoring(
    input_parquet: Path = PROCESSED_PARQUET_PATH,
    output_parquet: Path = PRISM_SCORED_PARQUET_PATH,
) -> Dict[str, Any]:
    """Runs batch PRISM scoring over input dataset and exports results.

    Args:
        input_parquet: Input parquet dataset path.
        output_parquet: Output parquet dataset path.

    Returns:
        Summary statistics dictionary.
    """
    if not input_parquet.exists():
        raise FileNotFoundError(
            f"Input preprocessed parquet not found at {input_parquet}"
        )

    df = pd.read_parquet(input_parquet)
    scored_df = score_dataframe(df)

    output_parquet.parent.mkdir(parents=True, exist_ok=True)
    scored_df.to_parquet(output_parquet, index=False)

    # Compute statistics
    total_records = len(scored_df)
    benign_df = (
        scored_df[scored_df["is_malicious"] == 0]
        if "is_malicious" in scored_df.columns
        else pd.DataFrame()
    )
    malicious_df = (
        scored_df[scored_df["is_malicious"] == 1]
        if "is_malicious" in scored_df.columns
        else pd.DataFrame()
    )

    mean_benign = float(benign_df["prism_score"].mean()) if not benign_df.empty else 0.0
    mean_malicious = (
        float(malicious_df["prism_score"].mean()) if not malicious_df.empty else 0.0
    )

    bucket_counts = scored_df["prism_risk_level"].value_counts().to_dict()

    malicious_high_crit = 0.0
    if not malicious_df.empty:
        high_crit_count = len(
            malicious_df[malicious_df["prism_risk_level"].isin(["HIGH", "CRITICAL"])]
        )
        malicious_high_crit = float((high_crit_count / len(malicious_df)) * 100.0)

    stats = {
        "total_records": total_records,
        "mean_benign_score": round(mean_benign, 4),
        "mean_malicious_score": round(mean_malicious, 4),
        "score_diff": round(mean_malicious - mean_benign, 4),
        "bucket_counts": bucket_counts,
        "malicious_high_critical_pct": round(malicious_high_crit, 2),
        "output_path": str(output_parquet),
    }

    return stats


def main() -> None:
    """CLI entrypoint for batch PRISM scoring."""
    print("Running PRISM Batch Scoring over preprocessed CERT dataset...")
    stats = run_batch_scoring()
    print("\nBatch Scoring Completed Successfully!")
    print(f"Total Records Processed: {stats['total_records']:,}")
    print(f"Mean Score (Benign User-Days):    {stats['mean_benign_score']:.4f}")
    print(f"Mean Score (Malicious User-Days): {stats['mean_malicious_score']:.4f}")
    print(f"Score Separation Delta:           +{stats['score_diff']:.4f}")
    print(
        f"Malicious User-Days in High/Critical Bucket: {stats['malicious_high_critical_pct']}%"
    )
    print(f"Risk Bucket Breakdown: {stats['bucket_counts']}")
    print(f"Scored Dataset Saved To: {stats['output_path']}")


if __name__ == "__main__":
    main()
