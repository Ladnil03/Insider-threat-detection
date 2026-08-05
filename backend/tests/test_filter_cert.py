"""Unit Tests for CERT Dataset Filtering Script."""

import tempfile
from pathlib import Path

import pandas as pd

from data_pipeline.filter_cert import (
    extract_malicious_metadata,
    filter_csv_file,
    run_filtering_pipeline,
    sample_benign_users,
)


def test_extract_malicious_metadata_with_synthetic_csv() -> None:
    """Tests extraction of malicious user IDs and date ranges from mock insiders file."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        answers_dir = Path(tmp_dir)
        insiders_csv = answers_dir / "insiders.csv"

        # Create mock insiders CSV
        mock_data = pd.DataFrame(
            {
                "user": ["MAL-001", "MAL-002"],
                "start_date": ["2010-02-01 08:00:00", "2010-03-01 09:00:00"],
                "end_date": ["2010-06-30 17:00:00", "2010-08-31 18:00:00"],
            }
        )
        mock_data.to_csv(insiders_csv, index=False)

        malicious_users, (min_date, max_date) = extract_malicious_metadata(answers_dir)

        assert "MAL-001" in malicious_users
        assert "MAL-002" in malicious_users
        assert min_date == pd.to_datetime("2010-02-01 08:00:00")
        assert max_date == pd.to_datetime("2010-08-31 18:00:00")


def test_sample_benign_users_reproducibility() -> None:
    """Tests that seeded benign sampling is deterministic and excludes malicious users."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        raw_dir = Path(tmp_dir)
        user_csv = raw_dir / "psychometric.csv"

        # Create synthetic user list
        mock_users = pd.DataFrame(
            {
                "user_id": [f"USR-{i:03d}" for i in range(100)],
                "user_name": [f"User {i}" for i in range(100)],
            }
        )
        mock_users.to_csv(user_csv, index=False)

        malicious_set = {"USR-001", "USR-002"}
        sampled_1 = sample_benign_users(
            raw_dir, malicious_set, benign_count=10, seed=42
        )
        sampled_2 = sample_benign_users(
            raw_dir, malicious_set, benign_count=10, seed=42
        )

        assert len(sampled_1) == 10
        assert sampled_1 == sampled_2
        assert "USR-001" not in sampled_1
        assert "USR-002" not in sampled_1


def test_filter_csv_file_chunked() -> None:
    """Tests chunked filtering of activity CSV by user and date window."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        input_csv = tmp_path / "logon.csv"
        output_csv = tmp_path / "filtered_logon.csv"

        # Create synthetic logon log entries
        mock_logon = pd.DataFrame(
            {
                "id": [1, 2, 3, 4],
                "date": [
                    "2010-03-01 08:00:00",
                    "2010-03-02 09:00:00",
                    "2010-03-03 10:00:00",
                    "2010-12-01 11:00:00",  # Out of date range
                ],
                "user": ["BEN-001", "BEN-002", "OUT-001", "BEN-001"],
                "pc": ["PC-1", "PC-2", "PC-3", "PC-1"],
                "activity": ["Logon", "Logon", "Logon", "Logoff"],
            }
        )
        mock_logon.to_csv(input_csv, index=False)

        target_users = {"BEN-001", "BEN-002"}
        date_bounds = (
            pd.to_datetime("2010-01-01"),
            pd.to_datetime("2010-06-30"),
        )
        usecols = ["id", "date", "user", "pc", "activity"]

        total_in, total_out = filter_csv_file(
            input_csv, output_csv, target_users, date_bounds, usecols, chunk_size=2
        )

        assert total_in == 4
        assert total_out == 2  # BEN-001 on 03-01 and BEN-002 on 03-02

        filtered_df = pd.read_csv(output_csv)
        assert len(filtered_df) == 2
        assert set(filtered_df["user"].unique()) == {"BEN-001", "BEN-002"}


def test_run_filtering_pipeline_end_to_end_synthetic() -> None:
    """Tests full execution of run_filtering_pipeline on synthetic folder structure."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        raw_dir = root / "raw"
        out_dir = root / "filtered"
        ans_dir = raw_dir / "answers"
        raw_dir.mkdir(parents=True)
        ans_dir.mkdir(parents=True)

        # Write mock files
        pd.DataFrame(
            {"user": ["M-1"], "start": ["2010-01-01"], "end": ["2010-05-01"]}
        ).to_csv(ans_dir / "insiders.csv", index=False)
        pd.DataFrame({"user_id": ["M-1", "B-1", "B-2"]}).to_csv(
            raw_dir / "psychometric.csv", index=False
        )
        pd.DataFrame(
            {
                "id": [101, 102],
                "date": ["2010-02-01 09:00:00", "2010-03-01 10:00:00"],
                "user": ["M-1", "B-1"],
                "pc": ["PC-1", "PC-2"],
                "activity": ["Logon", "Logon"],
            }
        ).to_csv(raw_dir / "logon.csv", index=False)

        summary = run_filtering_pipeline(
            raw_dir=raw_dir,
            output_dir=out_dir,
            answers_dir=ans_dir,
            benign_count=2,
            seed=42,
        )

        assert summary["malicious_user_count"] == 1
        assert summary["benign_user_count"] == 2
        assert (out_dir / "logon.csv").exists()
