"""Module for subsampling the CERT Insider Threat Dataset r4.2."""

import argparse
import logging
import random
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

import pandas as pd

from data_pipeline.config import (
    ANSWERS_DATA_DIR,
    CHUNK_SIZE,
    DEFAULT_BENIGN_USER_COUNT,
    DEFAULT_END_DATE,
    DEFAULT_RANDOM_SEED,
    DEFAULT_START_DATE,
    DEVICE_CSV,
    DEVICE_USECOLS,
    EMAIL_CSV,
    EMAIL_USECOLS,
    FILE_CSV,
    FILE_USECOLS,
    FILTERED_DATA_DIR,
    INSIDERS_CSV,
    LOGON_CSV,
    LOGON_USECOLS,
    RAW_DATA_DIR,
    USER_CSV,
    WEB_CSV,
    WEB_USECOLS,
)

# Configure module logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def extract_malicious_metadata(
    answers_dir: Path = ANSWERS_DATA_DIR,
) -> Tuple[Set[str], Tuple[pd.Timestamp, pd.Timestamp]]:
    """Extracts malicious user IDs and scenario date bounds from CERT answers.

    Args:
        answers_dir: Path to directory containing answers/insiders.csv.

    Returns:
        Tuple containing set of malicious user IDs and (min_date, max_date) bounds.
    """
    insiders_path = answers_dir / INSIDERS_CSV
    malicious_users: Set[str] = set()

    min_date = pd.to_datetime(DEFAULT_START_DATE)
    max_date = pd.to_datetime(DEFAULT_END_DATE)

    if insiders_path.exists():
        logger.info(f"Reading malicious user metadata from {insiders_path}")
        df = pd.read_csv(insiders_path)
        # Parse user column (e.g., 'user' or 'user_id')
        user_col = "user" if "user" in df.columns else df.columns[0]
        malicious_users.update(df[user_col].astype(str).unique())

        # Parse start and end date ranges if present
        date_cols = [
            c for c in df.columns if "start" in c.lower() or "end" in c.lower()
        ]
        if len(date_cols) >= 2:
            start_series = pd.to_datetime(df[date_cols[0]], errors="coerce")
            end_series = pd.to_datetime(df[date_cols[1]], errors="coerce")
            if not start_series.dropna().empty:
                min_date = start_series.min()
            if not end_series.dropna().empty:
                max_date = end_series.max()

    return malicious_users, (min_date, max_date)


def sample_benign_users(
    raw_dir: Path = RAW_DATA_DIR,
    malicious_users: Set[str] = set(),
    benign_count: int = DEFAULT_BENIGN_USER_COUNT,
    seed: int = DEFAULT_RANDOM_SEED,
) -> Set[str]:
    """Randomly samples benign user IDs excluding known malicious users.

    Args:
        raw_dir: Path to raw CERT CSV directory.
        malicious_users: Set of known malicious user IDs to exclude.
        benign_count: Target number of benign users to sample.
        seed: Random seed for reproducibility.

    Returns:
        Set of sampled benign user IDs.
    """
    all_users: Set[str] = set()

    # Try reading from psychometric.csv or extract from logon.csv
    user_file = raw_dir / USER_CSV
    logon_file = raw_dir / LOGON_CSV

    if user_file.exists():
        df_users = pd.read_csv(user_file)
        user_col = "user_id" if "user_id" in df_users.columns else "user"
        if user_col in df_users.columns:
            all_users.update(df_users[user_col].astype(str).unique())

    if not all_users and logon_file.exists():
        # Fallback chunked read to discover users from logon.csv
        for chunk in pd.read_csv(logon_file, chunksize=CHUNK_SIZE, usecols=["user"]):
            all_users.update(chunk["user"].astype(str).unique())

    benign_candidates = sorted(list(all_users - malicious_users))
    random.seed(seed)

    if len(benign_candidates) <= benign_count:
        sampled_benign = set(benign_candidates)
    else:
        sampled_benign = set(random.sample(benign_candidates, benign_count))

    logger.info(f"Sampled {len(sampled_benign)} benign users with seed={seed}")
    return sampled_benign


def filter_csv_file(
    input_path: Path,
    output_path: Path,
    target_users: Set[str],
    date_bounds: Tuple[pd.Timestamp, pd.Timestamp],
    usecols: List[str],
    chunk_size: int = CHUNK_SIZE,
) -> Tuple[int, int]:
    """Filters a single CSV file by target user cohort and date bounds using chunked reads.

    Args:
        input_path: Source raw CSV path.
        output_path: Destination filtered CSV path.
        target_users: Union of benign and malicious user IDs.
        date_bounds: (min_date, max_date) timestamp bounds.
        usecols: List of column names to load.
        chunk_size: Row chunk size per read iteration.

    Returns:
        Tuple of (total_input_rows, total_filtered_rows).
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        logger.warning(f"File {input_path} not found. Creating empty file stub.")
        pd.DataFrame(columns=usecols).to_csv(output_path, index=False)
        return 0, 0

    total_input = 0
    total_filtered = 0
    min_date, max_date = date_bounds
    first_chunk = True

    for chunk in pd.read_csv(input_path, chunksize=chunk_size, usecols=usecols):
        total_input += len(chunk)

        # Filter by user
        chunk["user"] = chunk["user"].astype(str)
        filtered = chunk[chunk["user"].isin(target_users)].copy()

        # Filter by date window if date column present
        if "date" in filtered.columns and not filtered.empty:
            filtered["date_dt"] = pd.to_datetime(filtered["date"], errors="coerce")
            filtered = filtered[
                (filtered["date_dt"] >= min_date) & (filtered["date_dt"] <= max_date)
            ]
            filtered = filtered.drop(columns=["date_dt"])

        total_filtered += len(filtered)

        mode = "w" if first_chunk else "a"
        header = first_chunk
        filtered.to_csv(output_path, mode=mode, header=header, index=False)
        first_chunk = False

    logger.info(
        f"Filtered {input_path.name}: {total_input} rows -> {total_filtered} rows"
    )
    return total_input, total_filtered


def run_filtering_pipeline(
    raw_dir: Path = RAW_DATA_DIR,
    output_dir: Path = FILTERED_DATA_DIR,
    answers_dir: Path = ANSWERS_DATA_DIR,
    benign_count: int = DEFAULT_BENIGN_USER_COUNT,
    seed: int = DEFAULT_RANDOM_SEED,
) -> Dict[str, Any]:
    """Executes end-to-end CERT dataset subsampling and chunked filtering pipeline.

    Args:
        raw_dir: Directory containing raw CERT CSV files.
        output_dir: Directory to store filtered output CSV files.
        answers_dir: Directory containing CERT answers metadata.
        benign_count: Target count of benign users to sample.
        seed: Random seed.

    Returns:
        Summary metrics dictionary.
    """
    logger.info("Starting CERT dataset filtering pipeline...")

    # 1. Auto-detect answers directory if default location doesn't exist
    if not answers_dir.exists():
        if (raw_dir / "answers").exists():
            answers_dir = raw_dir / "answers"
        elif (raw_dir.parent / "answers").exists():
            answers_dir = raw_dir.parent / "answers"

    # Extract malicious metadata
    malicious_users, date_bounds = extract_malicious_metadata(answers_dir)
    logger.info(
        f"Extracted {len(malicious_users)} malicious users. "
        f"Observation window: {date_bounds[0]} to {date_bounds[1]}"
    )

    # 2. Sample benign user cohort
    benign_users = sample_benign_users(raw_dir, malicious_users, benign_count, seed)
    target_users = malicious_users.union(benign_users)
    logger.info(
        f"Total cohort size: {len(target_users)} users "
        f"({len(benign_users)} benign, {len(malicious_users)} malicious)"
    )

    # 3. Filter each log source CSV in chunks
    files_to_process = [
        (LOGON_CSV, LOGON_USECOLS),
        (FILE_CSV, FILE_USECOLS),
        (DEVICE_CSV, DEVICE_USECOLS),
        (EMAIL_CSV, EMAIL_USECOLS),
        (WEB_CSV, WEB_USECOLS),
    ]

    summary_stats = {}
    for filename, usecols in files_to_process:
        inp = raw_dir / filename
        if filename == WEB_CSV and not inp.exists() and (raw_dir / "http.csv").exists():
            inp = raw_dir / "http.csv"
        out = output_dir / filename
        total_in, total_out = filter_csv_file(
            inp, out, target_users, date_bounds, usecols
        )
        file_size_mb = out.stat().st_size / (1024 * 1024) if out.exists() else 0.0
        summary_stats[filename] = {
            "input_rows": total_in,
            "filtered_rows": total_out,
            "output_size_mb": round(file_size_mb, 2),
        }

    pipeline_summary = {
        "malicious_user_count": len(malicious_users),
        "benign_user_count": len(benign_users),
        "total_target_users": len(target_users),
        "date_window_start": str(date_bounds[0]),
        "date_window_end": str(date_bounds[1]),
        "file_summary": summary_stats,
    }

    logger.info("CERT Dataset filtering pipeline complete.")
    return pipeline_summary


def main() -> None:
    """CLI argument parser entrypoint."""
    parser = argparse.ArgumentParser(
        description="Filter CERT Insider Threat Dataset r4.2 to benign/malicious user cohort."
    )
    parser.add_argument(
        "--benign-users",
        type=int,
        default=DEFAULT_BENIGN_USER_COUNT,
        help="Target number of benign users to sample (default: 300).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_RANDOM_SEED,
        help="Random seed for benign sampling (default: 42).",
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=RAW_DATA_DIR,
        help="Path to raw CERT CSV directory.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=FILTERED_DATA_DIR,
        help="Path to filtered output directory.",
    )

    args = parser.parse_args()
    summary = run_filtering_pipeline(
        raw_dir=args.raw_dir,
        output_dir=args.output_dir,
        benign_count=args.benign_users,
        seed=args.seed,
    )
    print("\n--- Pipeline Summary ---")
    for k, v in summary.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
