# Data Pipeline Module

This module handles ingestion, filtering, cleaning, daily feature engineering, and normalization of the CERT Insider Threat Dataset r4.2.

---

## 1. CERT Dataset Filter Script (`filter_cert.py`)

The dataset filtering script subsamples the raw CERT dataset (20GB+) down to a memory-efficient subset containing **all malicious users** and a randomly sampled **250–350 benign user cohort** over the scenario observation window.

### Key Features
- **Chunked Reading**: Uses `pandas.read_csv(chunksize=100000)` to stream large raw files without blowing up RAM.
- **Selective Column Extraction**: Extracts only necessary columns defined in `config.py` (`LOGON_USECOLS`, `FILE_USECOLS`, etc.).
- **Reproducible Sampling**: Uses deterministic random seed (default: 42).

### Running dataset filtering:
```bash
python -m data_pipeline.filter_cert --benign-users 300 --seed 42
```

---

## 2. Feature Extraction & Preprocessing Pipeline (`preprocess.py`)

The preprocessor ingests filtered activity log CSVs (`logon.csv`, `file.csv`, `device.csv`, `email.csv`, `web.csv`) and aggregates events into daily user activity records (`user`, `date_day`).

### Extracted Daily Feature Schema (72 Features Total)
1. **Base Daily Count Features (12)**:
   - **`logon_count`**: Total daily logons
   - **`logon_after_hours`**: Logons outside 08:00–18:00 or on weekends
   - **`file_count`**: Total file operations
   - **`file_copy_usb`**: File writes/copies to removable USB media
   - **`file_sensitive_access`**: File access on sensitive extensions (`.exe`, `.zip`, `.rar`, etc.)
   - **`device_connect_count`**: USB device connect events
   - **`device_disconnect_count`**: USB device disconnect events
   - **`email_count`**: Total emails sent/received
   - **`email_external_count`**: Emails sent to external recipient domains
   - **`email_large_attachment_count`**: Emails with attachments > 5 MB
   - **`web_visit_count`**: Total web page visits
   - **`web_job_search_count`**: Visits to job search portals (`indeed`, `glassdoor`, `linkedin`, etc.)

2. **Rolling Window Features (48)**:
   - **7-Day Rolling Mean & Std** (`{feature}_7d_mean`, `{feature}_7d_std`): Captures short-term activity volume spikes and recent variance.
   - **30-Day Rolling Mean & Std** (`{feature}_30d_mean`, `{feature}_30d_std`): Establishes medium-term user behavioral baselines.

3. **Baseline Deviation Features (12)**:
   - **30-Day Baseline Standardized Deviation** (`{feature}_baseline_dev`): Calculated per user as `(today's count - user's trailing 30-day mean) / user's trailing 30-day std` using `shift(1)` to ensure today's activity does not contaminate its own baseline.
   - **Cold-Start & Zero-Variance Handling Strategy**:
     - During the first 30 days for a user (history < 30 days), trailing statistics are undefined (`NaN`); baseline deviation is explicitly set to `0.0` (neutral deviation).
     - When historical variance is 0 (`std <= 1e-6`), unit scaling (`1.0`) is used so non-zero spikes relative to a constant baseline are correctly measured.

4. **Target & Partitioning Columns**:
   - **`is_malicious`**: Binary target (1 = malicious insider scenario day, 0 = benign day)
   - **`split`**: Partition label (`train`, `val`, `test`) derived from contiguous time windowing.

---

## 3. Contiguous Time-Based Split (`split_by_time`)

To prevent temporal data leakage (where future activity leaks into historical features via rolling averages), dataset partitioning strictly follows chronological time windows:
- **Train Split (70%)**: Earliest contiguous observation window.
- **Val Split (15%)**: Middle contiguous observation window.
- **Test Split (15%)**: Most recent contiguous observation window.
- **Zero Date Overlap**: Enforced zero date overlap between train, validation, and test sets.

---

## Artifact Outputs (`backend/data/filtered/processed/`)
- **`activity_features.parquet`**: Compressed parquet dataset containing all 72 daily activity features, `is_malicious` label, and `split` tag.
- **`encoding_config.json`**: Categorical schema, user mappings (`user_to_idx`), complete feature column lists, and class distribution metadata.
- **`split_metadata.json`**: Exact start/end boundary dates for train, val, and test contiguous partitions.

---

## Running Unit Tests
```bash
python -m pytest tests/test_filter_cert.py
python -m pytest tests/test_preprocess.py
```
