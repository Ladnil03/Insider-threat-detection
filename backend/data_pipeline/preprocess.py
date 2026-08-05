"""Module for dataset cleaning, daily feature aggregation, and categorical encoding."""

import argparse
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

import numpy as np
import pandas as pd

from data_pipeline.config import (
    ALL_FEATURE_COLS,
    ANSWERS_DATA_DIR,
    BASE_FEATURE_COLS,
    DEVICE_CSV,
    EMAIL_CSV,
    ENCODING_CONFIG_PATH,
    FILE_CSV,
    FILTERED_DATA_DIR,
    INSIDERS_CSV,
    JOB_SEARCH_KEYWORDS,
    LARGE_ATTACHMENT_BYTES,
    LOGON_CSV,
    PROCESSED_DATA_DIR,
    PROCESSED_PARQUET_PATH,
    SENSITIVE_EXTENSIONS,
    SPLIT_METADATA_PATH,
    WEB_CSV,
    WORK_HOURS_END,
    WORK_HOURS_START,
)

# Configure logger for preprocess module
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_filtered_csv(csv_path: Path) -> pd.DataFrame:
    """Loads a filtered CSV file, logs row count, and normalizes timestamp.

    Args:
        csv_path: Absolute or relative path to CSV file.

    Returns:
        DataFrame with normalized 'date' (Timestamp) and 'date_day' (str YYYY-MM-DD).
    """
    if not csv_path.exists():
        logger.warning(f"File {csv_path} does not exist. Returning empty DataFrame.")
        return pd.DataFrame()

    logger.info(f"Loading CSV: {csv_path}")
    df = pd.read_csv(csv_path)
    initial_rows = len(df)

    if df.empty:
        logger.warning(f"File {csv_path} is empty.")
        return df

    # Drop rows missing essential user or timestamp identifiers
    essential_cols = [c for c in ["user", "date"] if c in df.columns]
    if essential_cols:
        before_drop = len(df)
        df = df.dropna(subset=essential_cols).copy()
        dropped = before_drop - len(df)
        if dropped > 0:
            logger.info(
                f"Dropped {dropped}/{before_drop} rows missing essential columns {essential_cols} in {csv_path.name}"
            )

    # Normalize timestamp to UTC datetime
    if "date" in df.columns:
        df["date_dt"] = pd.to_datetime(df["date"], errors="coerce")
        invalid_dates = df["date_dt"].isna().sum()
        if invalid_dates > 0:
            logger.info(
                f"Dropping {invalid_dates} rows with unparseable date strings in {csv_path.name}"
            )
            df = df.dropna(subset=["date_dt"]).copy()

        df["date_day"] = df["date_dt"].dt.strftime("%Y-%m-%d")
        df["user"] = df["user"].astype(str)

    logger.info(
        f"Successfully loaded {csv_path.name}: {initial_rows} initial -> {len(df)} cleaned rows."
    )
    return df


def extract_malicious_user_days(
    answers_dir: Path,
) -> Tuple[Set[str], List[Dict[str, Any]]]:
    """Parses insiders.csv to extract malicious user IDs and scenario timelines.

    Args:
        answers_dir: Path to directory containing insiders.csv.

    Returns:
        Tuple containing set of malicious user IDs and list of scenario dicts.
    """
    insiders_file = answers_dir / INSIDERS_CSV
    malicious_users: Set[str] = set()
    scenarios: List[Dict[str, Any]] = []

    if not insiders_file.exists():
        logger.warning(
            f"Answers metadata file {insiders_file} not found. Returning empty scenario set."
        )
        return malicious_users, scenarios

    logger.info(f"Reading malicious user scenarios from {insiders_file}")
    df = pd.read_csv(insiders_file)
    user_col = "user" if "user" in df.columns else df.columns[0]
    malicious_users.update(df[user_col].astype(str).unique())

    for _, row in df.iterrows():
        user_id = str(row[user_col])
        start_date = None
        end_date = None
        for col in df.columns:
            if "start" in col.lower() and pd.notna(row[col]):
                start_date = pd.to_datetime(row[col], errors="coerce")
            elif "end" in col.lower() and pd.notna(row[col]):
                end_date = pd.to_datetime(row[col], errors="coerce")

        scenarios.append(
            {
                "user": user_id,
                "start_date": start_date,
                "end_date": end_date,
                "scenario": row.get("scenario", 1),
            }
        )

    return malicious_users, scenarios


def compute_daily_logon_features(logon_df: pd.DataFrame) -> pd.DataFrame:
    """Computes daily logon activity features per user per day.

    Args:
        logon_df: Cleaned logon events DataFrame.

    Returns:
        DataFrame indexed by (user, date_day) with logon feature metrics.
    """
    if logon_df.empty:
        return pd.DataFrame(
            columns=["user", "date_day", "logon_count", "logon_after_hours"]
        )

    # Calculate after-hours flag (outside 08:00-18:00 or Saturday/Sunday)
    hours = logon_df["date_dt"].dt.hour
    weekdays = logon_df["date_dt"].dt.weekday  # 5=Sat, 6=Sun
    logon_df["is_after_hours"] = (
        (hours < WORK_HOURS_START) | (hours >= WORK_HOURS_END) | (weekdays >= 5)
    )

    grouped = (
        logon_df.groupby(["user", "date_day"])
        .agg(
            logon_count=("id", "count"),
            logon_after_hours=("is_after_hours", "sum"),
        )
        .reset_index()
    )
    return grouped


def compute_daily_file_features(file_df: pd.DataFrame) -> pd.DataFrame:
    """Computes daily file system activity features per user per day.

    Args:
        file_df: Cleaned file events DataFrame.

    Returns:
        DataFrame indexed by (user, date_day) with file activity metrics.
    """
    if file_df.empty:
        return pd.DataFrame(
            columns=[
                "user",
                "date_day",
                "file_count",
                "file_copy_usb",
                "file_sensitive_access",
            ]
        )

    filename_str = file_df["filename"].fillna("").astype(str).str.lower()

    # Sensitive file extension detection
    is_sensitive = filename_str.apply(
        lambda fname: any(fname.endswith(ext) for ext in SENSITIVE_EXTENSIONS)
    )
    file_df["is_sensitive"] = is_sensitive

    # Detect copy to USB / external drive
    activity_str = (
        file_df["activity"].fillna("").astype(str).str.lower()
        if "activity" in file_df.columns
        else pd.Series("", index=file_df.index)
    )
    is_usb_copy = filename_str.str.startswith(
        ("e:", "f:", "g:", "h:", "/media")
    ) | activity_str.str.contains("copy|usb|removable")
    file_df["is_usb_copy"] = is_usb_copy

    grouped = (
        file_df.groupby(["user", "date_day"])
        .agg(
            file_count=("id", "count"),
            file_copy_usb=("is_usb_copy", "sum"),
            file_sensitive_access=("is_sensitive", "sum"),
        )
        .reset_index()
    )
    return grouped


def compute_daily_device_features(device_df: pd.DataFrame) -> pd.DataFrame:
    """Computes daily USB device connect/disconnect features per user per day.

    Args:
        device_df: Cleaned device events DataFrame.

    Returns:
        DataFrame indexed by (user, date_day) with device metrics.
    """
    if device_df.empty:
        return pd.DataFrame(
            columns=[
                "user",
                "date_day",
                "device_connect_count",
                "device_disconnect_count",
            ]
        )

    activity_str = device_df["activity"].fillna("").astype(str).str.lower()
    device_df["is_connect"] = activity_str.str.contains(
        "connect"
    ) & ~activity_str.str.contains("disconnect")
    device_df["is_disconnect"] = activity_str.str.contains("disconnect")

    grouped = (
        device_df.groupby(["user", "date_day"])
        .agg(
            device_connect_count=("is_connect", "sum"),
            device_disconnect_count=("is_disconnect", "sum"),
        )
        .reset_index()
    )
    return grouped


def compute_daily_email_features(email_df: pd.DataFrame) -> pd.DataFrame:
    """Computes daily email activity features per user per day.

    Args:
        email_df: Cleaned email events DataFrame.

    Returns:
        DataFrame indexed by (user, date_day) with email metrics.
    """
    if email_df.empty:
        return pd.DataFrame(
            columns=[
                "user",
                "date_day",
                "email_count",
                "email_external_count",
                "email_large_attachment_count",
            ]
        )

    # Detect external recipients
    to_str = email_df["to"].fillna("").astype(str).str.lower()

    # Extract internal domain from 'from' address or check known internal domains
    internal_domains = ["@doolittle.com", "@dsa.com"]
    email_df["is_external"] = to_str.apply(
        lambda t: not any(dom in t for dom in internal_domains) if t else False
    )

    # Detect large attachments
    size_num = pd.to_numeric(email_df["size"], errors="coerce").fillna(0)
    email_df["is_large_attachment"] = size_num > LARGE_ATTACHMENT_BYTES

    grouped = (
        email_df.groupby(["user", "date_day"])
        .agg(
            email_count=("id", "count"),
            email_external_count=("is_external", "sum"),
            email_large_attachment_count=("is_large_attachment", "sum"),
        )
        .reset_index()
    )
    return grouped


def compute_daily_web_features(web_df: pd.DataFrame) -> pd.DataFrame:
    """Computes daily web browsing activity features per user per day.

    Args:
        web_df: Cleaned web/HTTP events DataFrame.

    Returns:
        DataFrame indexed by (user, date_day) with web metrics.
    """
    if web_df.empty:
        return pd.DataFrame(
            columns=["user", "date_day", "web_visit_count", "web_job_search_count"]
        )

    url_str = web_df["url"].fillna("").astype(str).str.lower()
    is_job_search = url_str.apply(lambda u: any(kw in u for kw in JOB_SEARCH_KEYWORDS))
    web_df["is_job_search"] = is_job_search

    grouped = (
        web_df.groupby(["user", "date_day"])
        .agg(
            web_visit_count=("id", "count"),
            web_job_search_count=("is_job_search", "sum"),
        )
        .reset_index()
    )
    return grouped


def compute_rolling_features(
    df: pd.DataFrame, feature_cols: List[str] = BASE_FEATURE_COLS
) -> pd.DataFrame:
    """Computes 7-day and 30-day rolling mean and std features per user.

    Args:
        df: Daily user feature matrix containing base feature columns.
        feature_cols: List of base feature column names to compute rolling metrics on.

    Returns:
        DataFrame with added rolling feature columns.
    """
    logger.info("Computing 7-day and 30-day rolling mean and std features per user...")
    df = df.sort_values(by=["user", "date_day"]).copy()

    for col in feature_cols:
        if col not in df.columns:
            continue

        # 7-day rolling mean and std
        df[f"{col}_7d_mean"] = (
            df.groupby("user")[col]
            .transform(lambda s: s.rolling(window=7, min_periods=1).mean())
            .astype(np.float32)
        )
        df[f"{col}_7d_std"] = (
            df.groupby("user")[col]
            .transform(lambda s: s.rolling(window=7, min_periods=1).std())
            .fillna(0.0)
            .astype(np.float32)
        )

        # 30-day rolling mean and std
        df[f"{col}_30d_mean"] = (
            df.groupby("user")[col]
            .transform(lambda s: s.rolling(window=30, min_periods=1).mean())
            .astype(np.float32)
        )
        df[f"{col}_30d_std"] = (
            df.groupby("user")[col]
            .transform(lambda s: s.rolling(window=30, min_periods=1).std())
            .fillna(0.0)
            .astype(np.float32)
        )

    return df


def compute_baseline_deviation_features(
    df: pd.DataFrame, feature_cols: List[str] = BASE_FEATURE_COLS
) -> pd.DataFrame:
    """Computes 30-day standardized baseline deviation features per user.

    Formula: (today's value - user's trailing 30-day mean) / user's trailing 30-day std.

    Cold-Start & Zero-Variance Handling Strategy:
        - Cold-Start Window (history < 30 days): When trailing history has fewer than 30 days
          (min_periods=30), trailing_mean and trailing_std are NaN. In this cold-start window,
          baseline deviation is explicitly set to 0.0 (neutral deviation).
        - Zero-Variance Baseline (trailing_std <= 1e-6): If historical activity was perfectly constant
          (std ~ 0.0), unit scaling (1.0) is used so that non-zero activity spikes relative to the constant
          baseline are correctly captured rather than zeroed out.

    Args:
        df: Daily user feature matrix containing base feature columns.
        feature_cols: Base feature columns to calculate deviation for.

    Returns:
        DataFrame with added baseline deviation feature columns.
    """
    logger.info("Computing per-user 30-day baseline deviation features...")
    df = df.sort_values(by=["user", "date_day"]).copy()

    for col in feature_cols:
        if col not in df.columns:
            continue

        # Use shift(1) so today's activity spike does not pollute its own baseline
        trailing_mean = df.groupby("user")[col].transform(
            lambda s: s.shift(1).rolling(window=30, min_periods=30).mean()
        )
        trailing_std = df.groupby("user")[col].transform(
            lambda s: s.shift(1).rolling(window=30, min_periods=30).std()
        )

        # Scale by trailing_std if std > 1e-6, else unit scale 1.0
        effective_std = np.where(
            trailing_std > 1e-6,
            trailing_std,
            np.where(trailing_std.notna(), 1.0, np.nan),
        )

        deviation = (df[col] - trailing_mean) / effective_std
        # Cold start (where trailing_mean / trailing_std is NaN) is set explicitly to 0.0
        df[f"{col}_baseline_dev"] = (
            pd.Series(deviation, index=df.index).fillna(0.0).astype(np.float32)
        )

    return df


def split_by_time(
    df: pd.DataFrame,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Splits dataset by contiguous time windows into train, validation, and test sets.

    Ensures zero date overlap between train, val, and test splits to prevent future leak.

    Args:
        df: Feature DataFrame with 'date_day' column.
        train_ratio: Fraction of date span for training.
        val_ratio: Fraction of date span for validation.
        test_ratio: Fraction of date span for testing.

    Returns:
        Tuple of (DataFrame with added 'split' column, split metadata dict).
    """
    logger.info("Performing contiguous time-based dataset split...")
    df = df.sort_values(by=["date_day", "user"]).reset_index(drop=True)

    unique_dates = sorted(df["date_day"].unique().tolist())
    n_dates = len(unique_dates)

    if n_dates == 0:
        logger.warning("Empty dataset passed to split_by_time.")
        return df, {}

    n_train = max(1, int(n_dates * train_ratio))
    n_val = max(1, int(n_dates * val_ratio))

    train_dates = set(unique_dates[:n_train])
    val_dates = set(unique_dates[n_train : n_train + n_val])

    def assign_split(date_str: str) -> str:
        if date_str in train_dates:
            return "train"
        elif date_str in val_dates:
            return "val"
        else:
            return "test"

    df["split"] = df["date_day"].apply(assign_split)

    split_metadata = {
        "train_start": unique_dates[0],
        "train_end": unique_dates[n_train - 1],
        "val_start": unique_dates[n_train] if n_train < n_dates else None,
        "val_end": (
            unique_dates[n_train + n_val - 1]
            if (n_train + n_val - 1) < n_dates
            else None
        ),
        "test_start": (
            unique_dates[n_train + n_val] if (n_train + n_val) < n_dates else None
        ),
        "test_end": unique_dates[-1],
        "split_ratios": {
            "train": train_ratio,
            "val": val_ratio,
            "test": test_ratio,
        },
        "counts": {
            "train": int((df["split"] == "train").sum()),
            "val": int((df["split"] == "val").sum()),
            "test": int((df["split"] == "test").sum()),
        },
        "malicious_counts": {
            "train": int(((df["split"] == "train") & (df["is_malicious"] == 1)).sum()),
            "val": int(((df["split"] == "val") & (df["is_malicious"] == 1)).sum()),
            "test": int(((df["split"] == "test") & (df["is_malicious"] == 1)).sum()),
        },
    }

    logger.info(
        f"Time split complete: Train ({split_metadata['train_start']} to {split_metadata['train_end']} -> {split_metadata['counts']['train']} rows), "
        f"Val ({split_metadata['val_start']} to {split_metadata['val_end']} -> {split_metadata['counts']['val']} rows), "
        f"Test ({split_metadata['test_start']} to {split_metadata['test_end']} -> {split_metadata['counts']['test']} rows)"
    )

    return df, split_metadata


def _discover_user_day_pairs(dfs: List[pd.DataFrame]) -> Set[Tuple[str, str]]:
    """Discovers unique (user, date_day) pairs across all dataframes.

    Args:
        dfs: List of log activity DataFrames.

    Returns:
        Set of unique (user, date_day) tuples.
    """
    user_day_pairs: Set[Tuple[str, str]] = set()
    for df in dfs:
        if not df.empty and "user" in df.columns and "date_day" in df.columns:
            user_day_pairs.update(
                zip(df["user"].astype(str), df["date_day"].astype(str))
            )
    return user_day_pairs


def _resolve_answers_dir(answers_dir: Path, input_dir: Path) -> Path:
    """Resolves answers directory location across standard and cache paths.

    Args:
        answers_dir: Preferred answers path.
        input_dir: Input raw or filtered data path.

    Returns:
        Resolved Path containing insiders.csv.
    """
    kaggle_answers = Path(
        "C:/Users/ladni/.cache/kagglehub/datasets/andrihjonior/cert-insider-threat-dataset-r4-2/versions/1/answers"
    )
    if not (answers_dir / INSIDERS_CSV).exists():
        if (input_dir / "answers" / INSIDERS_CSV).exists():
            return input_dir / "answers"
        if (input_dir.parent / "answers" / INSIDERS_CSV).exists():
            return input_dir.parent / "answers"
        if (kaggle_answers / INSIDERS_CSV).exists():
            return kaggle_answers
    return answers_dir


def build_daily_feature_matrix(
    input_dir: Path = FILTERED_DATA_DIR,
    answers_dir: Path = ANSWERS_DATA_DIR,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Merges all log sources into a unified daily user activity feature matrix.

    Args:
        input_dir: Directory containing filtered CSV files.
        answers_dir: Directory containing insiders.csv metadata.

    Returns:
        Tuple of (unified feature DataFrame, encoding schema dict).
    """
    logger.info("Starting daily feature extraction & preprocessing pipeline...")

    # Load filtered CSV files
    dfs = [
        load_filtered_csv(input_dir / LOGON_CSV),
        load_filtered_csv(input_dir / FILE_CSV),
        load_filtered_csv(input_dir / DEVICE_CSV),
        load_filtered_csv(input_dir / EMAIL_CSV),
        load_filtered_csv(input_dir / WEB_CSV),
    ]

    # 1. Discover all unique (user, date_day) combinations
    user_day_pairs = _discover_user_day_pairs(dfs)
    if not user_day_pairs:
        logger.warning("No activity records discovered across input CSV files.")
        return pd.DataFrame(), {}

    logger.info(f"Discovered {len(user_day_pairs)} total user-day activity pairs.")

    base_df = (
        pd.DataFrame(list(user_day_pairs), columns=["user", "date_day"])
        .sort_values(by=["user", "date_day"])
        .reset_index(drop=True)
    )

    # 2. Compute feature aggregations per domain
    logon_feats = compute_daily_logon_features(dfs[0])
    file_feats = compute_daily_file_features(dfs[1])
    device_feats = compute_daily_device_features(dfs[2])
    email_feats = compute_daily_email_features(dfs[3])
    web_feats = compute_daily_web_features(dfs[4])

    # 3. Outer join domain feature sets onto base (user, date_day) matrix
    feature_df = base_df.merge(logon_feats, on=["user", "date_day"], how="left")
    feature_df = feature_df.merge(file_feats, on=["user", "date_day"], how="left")
    feature_df = feature_df.merge(device_feats, on=["user", "date_day"], how="left")
    feature_df = feature_df.merge(email_feats, on=["user", "date_day"], how="left")
    feature_df = feature_df.merge(web_feats, on=["user", "date_day"], how="left")

    # 4. Fill missing base numeric features with 0 (imputation strategy)
    for col in BASE_FEATURE_COLS:
        if col in feature_df.columns:
            null_count = feature_df[col].isna().sum()
            if null_count > 0:
                feature_df[col] = feature_df[col].fillna(0).astype(np.float32)
                logger.info(f"Imputed {null_count} NaNs in feature '{col}' with 0.0")

    # 5. Compute rolling 7-day and 30-day mean & std features per user
    feature_df = compute_rolling_features(feature_df, BASE_FEATURE_COLS)

    # 6. Compute 30-day standardized baseline deviation features per user
    feature_df = compute_baseline_deviation_features(feature_df, BASE_FEATURE_COLS)

    # 7. Malicious user scenario target labeling
    resolved_answers = _resolve_answers_dir(answers_dir, input_dir)
    malicious_users, scenarios = extract_malicious_user_days(resolved_answers)
    feature_df["is_malicious"] = 0

    feature_df["date_dt"] = pd.to_datetime(feature_df["date_day"])
    for sc in scenarios:
        u = sc["user"]
        st = sc["start_date"]
        et = sc["end_date"]
        mask = feature_df["user"] == u
        if st is not None:
            mask = mask & (feature_df["date_dt"] >= st)
        if et is not None:
            mask = mask & (feature_df["date_dt"] <= et)
        feature_df.loc[mask, "is_malicious"] = 1

    feature_df = feature_df.drop(columns=["date_dt"])
    malicious_days = (feature_df["is_malicious"] == 1).sum()
    logger.info(
        f"Labeled dataset: {len(feature_df)} user-day records -> {malicious_days} malicious user-days."
    )

    # 8. Contiguous time-based train/val/test split
    feature_df, split_metadata = split_by_time(feature_df)

    # 9. Build categorical encoding schema & metadata
    unique_users = sorted(feature_df["user"].unique().tolist())
    user_to_idx = {user_id: idx for idx, user_id in enumerate(unique_users)}

    encoding_schema = {
        "user_to_idx": user_to_idx,
        "base_feature_columns": BASE_FEATURE_COLS,
        "feature_columns": ALL_FEATURE_COLS,
        "target_column": "is_malicious",
        "split_column": "split",
        "total_records": len(feature_df),
        "malicious_records": int(malicious_days),
        "benign_records": int(len(feature_df) - malicious_days),
        "split_metadata": split_metadata,
    }

    return feature_df, encoding_schema


def save_processed_data(
    df: pd.DataFrame,
    encoding_schema: Dict[str, Any],
    parquet_path: Path = PROCESSED_PARQUET_PATH,
    config_path: Path = ENCODING_CONFIG_PATH,
    split_config_path: Path = SPLIT_METADATA_PATH,
) -> None:
    """Exports processed DataFrame to parquet and saves encoding config JSON and split metadata JSON.

    Args:
        df: Preprocessed feature DataFrame.
        encoding_schema: Dictionary containing categorical encodings and metadata.
        parquet_path: Output parquet file path.
        config_path: Output encoding config JSON path.
        split_config_path: Output split metadata JSON path.
    """
    parquet_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    split_config_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Saving preprocessed DataFrame to parquet: {parquet_path}")
    try:
        df.to_parquet(parquet_path, engine="fastparquet", index=False)
    except Exception as e:
        logger.warning(
            f"fastparquet export failed ({e}), attempting pyarrow default engine..."
        )
        df.to_parquet(parquet_path, index=False)

    logger.info(f"Saving encoding configuration JSON: {config_path}")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(encoding_schema, f, indent=2)

    if "split_metadata" in encoding_schema:
        logger.info(f"Saving time-based split metadata JSON: {split_config_path}")
        with open(split_config_path, "w", encoding="utf-8") as f:
            json.dump(encoding_schema["split_metadata"], f, indent=2)

    logger.info("Successfully exported preprocessed pipeline artifacts.")


def main() -> None:
    """CLI entrypoint for running the preprocessing pipeline."""
    parser = argparse.ArgumentParser(
        description="Preprocess filtered CERT dataset into daily user feature matrix."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=FILTERED_DATA_DIR,
        help="Directory containing filtered CSV files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROCESSED_DATA_DIR,
        help="Directory to store processed parquet output.",
    )

    args = parser.parse_args()
    feature_df, encoding_schema = build_daily_feature_matrix(
        input_dir=args.input_dir,
    )

    if not feature_df.empty:
        parquet_out = args.output_dir / "activity_features.parquet"
        config_out = args.output_dir / "encoding_config.json"
        split_out = args.output_dir / "split_metadata.json"
        save_processed_data(
            feature_df, encoding_schema, parquet_out, config_out, split_out
        )
        print("\n--- Preprocessing Pipeline Complete ---")
        print(f"Total Daily Records: {len(feature_df)}")
        print(f"Total Features Extracted: {len(ALL_FEATURE_COLS)}")
        print(f"Malicious User-Days: {encoding_schema['malicious_records']}")
        print(f"Parquet Output: {parquet_out}")
        print(f"Encoding Schema: {config_out}")
        print(f"Split Metadata: {split_out}")


if __name__ == "__main__":
    main()
