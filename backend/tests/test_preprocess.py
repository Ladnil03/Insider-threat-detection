"""Unit tests for dataset preprocessing and feature extraction module."""

import json
from pathlib import Path

import pandas as pd
import pytest

from data_pipeline.preprocess import (
    compute_baseline_deviation_features,
    compute_daily_device_features,
    compute_daily_email_features,
    compute_daily_file_features,
    compute_daily_logon_features,
    compute_daily_web_features,
    compute_rolling_features,
    load_filtered_csv,
    save_processed_data,
    split_by_time,
)


@pytest.fixture
def synthetic_logon_df() -> pd.DataFrame:
    """Fixture providing synthetic logon events DataFrame."""
    data = {
        "id": ["L1", "L2", "L3"],
        "date": ["2010-05-03 09:00:00", "2010-05-03 22:00:00", "2010-05-04 10:00:00"],
        "user": ["U1001", "U1001", "U1002"],
        "pc": ["PC1", "PC1", "PC2"],
        "activity": ["Logon", "Logon", "Logon"],
    }
    df = pd.DataFrame(data)
    df["date_dt"] = pd.to_datetime(df["date"])
    df["date_day"] = df["date_dt"].dt.strftime("%Y-%m-%d")
    return df


@pytest.fixture
def synthetic_file_df() -> pd.DataFrame:
    """Fixture providing synthetic file activity events DataFrame."""
    data = {
        "id": ["F1", "F2", "F3"],
        "date": ["2010-05-01 10:00:00", "2010-05-01 11:00:00", "2010-05-02 12:00:00"],
        "user": ["U1001", "U1001", "U1002"],
        "pc": ["PC1", "PC1", "PC2"],
        "filename": ["E:\\sensitive.exe", "report.pdf", "data.zip"],
        "activity": ["file copy", "file open", "file copy"],
    }
    df = pd.DataFrame(data)
    df["date_dt"] = pd.to_datetime(df["date"])
    df["date_day"] = df["date_dt"].dt.strftime("%Y-%m-%d")
    return df


def test_load_filtered_csv(tmp_path: Path):
    """Tests CSV loading, timestamp normalization, and missing row dropping."""
    csv_file = tmp_path / "test_logon.csv"
    data = {
        "id": ["1", "2", "3"],
        "date": ["2010-01-01 08:00:00", "invalid_date", "2010-01-02 14:00:00"],
        "user": ["U1", "U2", None],
    }
    pd.DataFrame(data).to_csv(csv_file, index=False)

    df = load_filtered_csv(csv_file)
    assert len(df) == 1  # Only row 1 has both valid user and valid date
    assert "date_day" in df.columns
    assert df["date_day"].iloc[0] == "2010-01-01"


def test_compute_daily_logon_features(synthetic_logon_df: pd.DataFrame):
    """Tests daily logon count and after-hours aggregation logic."""
    feats = compute_daily_logon_features(synthetic_logon_df)
    assert len(feats) == 2  # (U1001, 2010-05-01) and (U1002, 2010-05-02)

    u1_day1 = feats[(feats["user"] == "U1001") & (feats["date_day"] == "2010-05-03")]
    assert u1_day1["logon_count"].iloc[0] == 2
    assert u1_day1["logon_after_hours"].iloc[0] == 1  # 22:00 logon is after hours


def test_compute_daily_file_features(synthetic_file_df: pd.DataFrame):
    """Tests USB copy and sensitive extension feature aggregation."""
    feats = compute_daily_file_features(synthetic_file_df)
    u1_day1 = feats[(feats["user"] == "U1001") & (feats["date_day"] == "2010-05-01")]

    assert u1_day1["file_count"].iloc[0] == 2
    assert u1_day1["file_copy_usb"].iloc[0] == 1  # E:\ drive file copy
    assert u1_day1["file_sensitive_access"].iloc[0] == 1  # .exe extension


def test_compute_daily_device_features():
    """Tests device connect and disconnect event aggregation."""
    data = {
        "id": ["D1", "D2"],
        "date": ["2010-05-01 10:00:00", "2010-05-01 11:00:00"],
        "user": ["U1", "U1"],
        "activity": ["Connect", "Disconnect"],
    }
    df = pd.DataFrame(data)
    df["date_dt"] = pd.to_datetime(df["date"])
    df["date_day"] = df["date_dt"].dt.strftime("%Y-%m-%d")

    feats = compute_daily_device_features(df)
    assert feats["device_connect_count"].iloc[0] == 1
    assert feats["device_disconnect_count"].iloc[0] == 1


def test_compute_daily_email_features():
    """Tests email external recipient and large attachment aggregation."""
    data = {
        "id": ["E1", "E2"],
        "date": ["2010-05-01 10:00:00", "2010-05-01 11:00:00"],
        "user": ["U1", "U1"],
        "to": ["external@gmail.com", "internal@doolittle.com"],
        "from": ["user@doolittle.com", "user@doolittle.com"],
        "size": [10_000_000, 500],
    }
    df = pd.DataFrame(data)
    df["date_dt"] = pd.to_datetime(df["date"])
    df["date_day"] = df["date_dt"].dt.strftime("%Y-%m-%d")

    feats = compute_daily_email_features(df)
    assert feats["email_external_count"].iloc[0] == 1
    assert feats["email_large_attachment_count"].iloc[0] == 1


def test_compute_daily_web_features():
    """Tests web job search keyword detection feature aggregation."""
    data = {
        "id": ["W1", "W2"],
        "date": ["2010-05-01 10:00:00", "2010-05-01 11:00:00"],
        "user": ["U1", "U1"],
        "url": ["https://www.indeed.com/jobs", "https://www.wikipedia.org"],
    }
    df = pd.DataFrame(data)
    df["date_dt"] = pd.to_datetime(df["date"])
    df["date_day"] = df["date_dt"].dt.strftime("%Y-%m-%d")

    feats = compute_daily_web_features(df)
    assert feats["web_visit_count"].iloc[0] == 2
    assert feats["web_job_search_count"].iloc[0] == 1


def test_compute_rolling_features():
    """Tests 7-day and 30-day rolling mean and std feature calculation per user."""
    dates = pd.date_range("2010-01-01", periods=10).strftime("%Y-%m-%d")
    df = pd.DataFrame(
        {
            "user": ["U1"] * 10,
            "date_day": dates,
            "logon_count": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
        }
    )

    res = compute_rolling_features(df, feature_cols=["logon_count"])

    assert "logon_count_7d_mean" in res.columns
    assert "logon_count_7d_std" in res.columns
    assert "logon_count_30d_mean" in res.columns
    assert "logon_count_30d_std" in res.columns

    # First row 7-day mean should be 1.0
    assert res["logon_count_7d_mean"].iloc[0] == pytest.approx(1.0)
    # Row index 6 (7th item: 1..7) 7-day mean should be (1+2+3+4+5+6+7)/7 = 4.0
    assert res["logon_count_7d_mean"].iloc[6] == pytest.approx(4.0)


def test_compute_baseline_deviation_features():
    """Tests 30-day baseline deviation feature calculation and cold-start handling."""
    dates = pd.date_range("2010-01-01", periods=35).strftime("%Y-%m-%d")
    # First 30 days constant 10.0, day 31 spike to 50.0
    vals = [10.0] * 30 + [50.0, 10.0, 10.0, 10.0, 10.0]
    df = pd.DataFrame({"user": ["U1"] * 35, "date_day": dates, "file_count": vals})

    res = compute_baseline_deviation_features(df, feature_cols=["file_count"])

    assert "file_count_baseline_dev" in res.columns
    # First 30 days should be explicitly 0.0 (cold start or zero variance)
    assert res["file_count_baseline_dev"].iloc[0] == 0.0
    assert res["file_count_baseline_dev"].iloc[29] == 0.0
    # Day 31 (index 30) should have positive spike deviation
    assert res["file_count_baseline_dev"].iloc[30] > 0.0


def test_split_by_time_zero_date_overlap():
    """Tests contiguous time-based dataset split and verifies zero date overlap."""
    dates = pd.date_range("2010-01-01", periods=100).strftime("%Y-%m-%d")
    df = pd.DataFrame(
        {
            "user": ["U1"] * 100,
            "date_day": dates,
            "is_malicious": [0] * 90 + [1] * 10,
        }
    )

    res_df, split_meta = split_by_time(
        df, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15
    )

    assert "split" in res_df.columns
    train_dates = set(res_df[res_df["split"] == "train"]["date_day"])
    val_dates = set(res_df[res_df["split"] == "val"]["date_day"])
    test_dates = set(res_df[res_df["split"] == "test"]["date_day"])

    # Confirm ZERO date overlap
    assert len(train_dates.intersection(val_dates)) == 0
    assert len(train_dates.intersection(test_dates)) == 0
    assert len(val_dates.intersection(test_dates)) == 0

    # Confirm contiguous metadata
    assert split_meta["train_start"] == "2010-01-01"
    assert split_meta["train_end"] < split_meta["val_start"]
    assert split_meta["val_end"] < split_meta["test_start"]


def test_save_processed_data(tmp_path: Path):
    """Tests exporting processed feature matrix to parquet, config JSON, and split metadata JSON."""
    df = pd.DataFrame(
        {
            "user": ["U1", "U2"],
            "date_day": ["2010-05-01", "2010-05-01"],
            "logon_count": [1.0, 2.0],
            "is_malicious": [0, 1],
            "split": ["train", "train"],
        }
    )
    split_meta = {"train_start": "2010-05-01", "train_end": "2010-05-01"}
    encoding_schema = {
        "user_to_idx": {"U1": 0, "U2": 1},
        "total_records": 2,
        "split_metadata": split_meta,
    }

    parquet_out = tmp_path / "test.parquet"
    json_out = tmp_path / "test.json"
    split_out = tmp_path / "split.json"

    save_processed_data(df, encoding_schema, parquet_out, json_out, split_out)

    assert parquet_out.exists()
    assert json_out.exists()
    assert split_out.exists()

    loaded_df = pd.read_parquet(parquet_out)
    assert len(loaded_df) == 2
    assert "is_malicious" in loaded_df.columns
    assert "split" in loaded_df.columns

    with open(json_out, "r") as f:
        loaded_json = json.load(f)
    assert loaded_json["total_records"] == 2

    with open(split_out, "r") as f:
        loaded_split = json.load(f)
    assert loaded_split["train_start"] == "2010-05-01"
