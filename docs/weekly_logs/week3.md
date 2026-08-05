# Week 3 Completion Log: Data Preprocessing & Exploratory Data Analysis (EDA)

- **Date Completed**: 2026-08-04
- **Author**: Antigravity Assistant & OpenIRM Team

---

## 1. Files Created and Modified

### Backend Data Pipeline (`backend/data_pipeline/`)
- `backend/data_pipeline/config.py`: Added constants for processed data output paths (`PROCESSED_DATA_DIR`, `PROCESSED_PARQUET_PATH`, `ENCODING_CONFIG_PATH`), business hours (08:00–18:00), sensitive file extensions, large attachment thresholds, and job search keywords.
- `backend/data_pipeline/preprocess.py`: Implemented timestamp normalization (`load_filtered_csv`), daily feature extraction across domains (`compute_daily_logon_features`, `compute_daily_file_features`, `compute_daily_device_features`, `compute_daily_email_features`, `compute_daily_web_features`), missing value handling/imputation (`build_daily_feature_matrix`), insider scenario labeling, categorical encoding (`encoding_config.json`), fastparquet export (`save_processed_data`), and CLI interface (`main`).
- `backend/data_pipeline/generate_eda.py`: Implemented automated figure generator (`generate_eda_figures`) and Jupyter Notebook builder (`generate_eda_notebook`).
- `backend/data_pipeline/README.md`: Updated module documentation with feature definitions, imputation strategy, parquet output specs, and CLI commands.

### Dependencies & Tests (`backend/`, `backend/tests/`)
- `backend/requirements.txt`: Added `pyarrow`, `fastparquet`, `matplotlib`, and `seaborn` dependencies.
- `backend/tests/test_preprocess.py`: Created synthetic test suite covering timestamp parsing, logon after-hours counts, USB copy/sensitive file detection, device connect counts, external email logic, job search web detection, and parquet/JSON export.

### Documentation & Visualizations (`docs/`)
- `docs/eda.ipynb`: Jupyter notebook covering class balance, activity volume, time distribution, and scenario window sanity checks.
- `docs/eda_class_balance.png`: PNG plot of benign vs malicious user-day records.
- `docs/eda_activity_volume.png`: PNG plot of activity volume per user across logons, files, emails, and web visits.
- `docs/eda_time_distribution.png`: PNG plot of business hours vs off-hours/weekend logons.
- `docs/eda_scenario_timeline.png`: PNG plot verifying active malicious scenario timelines.
- `docs/weekly_logs/week3.md`: This completion log.

---

## 2. Implementation Summary

- **Daily Feature Aggregation**: Grouped event logs by `(user, date_day)` to extract daily feature vectors including `logon_count`, `logon_after_hours`, `file_copy_usb`, `file_sensitive_access`, `device_connect_count`, `email_external_count`, `email_large_attachment_count`, and `web_job_search_count`.
- **Missing Data Strategy**: Logged and dropped invalid timestamp/user records. Imputed missing numerical feature counts with `0.0` across joined activity domains.
- **Malicious Scenario Labeling**: Resolved insider scenario date windows from `insiders.csv` to flag 1,294 malicious user-day records out of 99,987 total user-days.
- **Parquet & Encoding Artifacts**: Exported unified dataset to `backend/data/filtered/processed/activity_features.parquet` (compressed) and categorical schema to `backend/data/filtered/processed/encoding_config.json`.
- **Exploratory Data Analysis (EDA)**: Generated 4 publication-ready PNG figures and an interactive `docs/eda.ipynb` notebook confirming zero scenario timeline truncation.

---

## 3. Deviations from Original Week 3 Prompt

- None. All tasks, CLI interface options, parquet export specs, EDA visualizations, unit tests, and documentation match the Week 3 task prompt requirements.

---

## 4. Test Results & Metrics

- **pytest suite**: Passed **19 / 19** tests (0 failures).
  - `tests/test_preprocess.py`: 7 passed (timestamp parsing, logon after-hours, USB file copy, device connects, email external rules, web job search, parquet/JSON serialization)
  - `tests/test_filter_cert.py`: 4 passed
  - `tests/test_prism.py`: 2 passed
  - `tests/test_airs.py`: 2 passed
  - `tests/test_explainability.py`: 1 passed
  - `tests/test_api.py`: 2 passed
  - `tests/test_policy_engine.py`: 1 passed
- **Preprocessed Output Metrics**:
  - Total Daily Records: **99,987 user-days**
  - Benign User-Days: **98,693** (98.71%)
  - Malicious User-Days: **1,294** (1.29%)
- **black & ruff checks**: 100% clean across all 50 Python backend files.

---

## 5. Known Issues / TODOs Carried Forward

- `backend/data/filtered/processed/activity_features.parquet` will be loaded in Week 4 by the PRISM rule engine to calculate domain sub-scores and baseline risk labels.
- PyTorch Autoencoder (AIRS) model training loop in Week 5+ will ingest the normalized feature vectors.

---

## 6. Commands to Verify This Week's Work

Run the following commands inside `backend/venv/`:

1. **Execute Preprocessing Pipeline CLI**:
   ```bash
   python -m data_pipeline.preprocess
   ```

2. **Generate EDA Figures & Notebook**:
   ```bash
   python -m data_pipeline.generate_eda
   ```

3. **Run Preprocessing Unit Tests**:
   ```bash
   python -m pytest tests/test_preprocess.py
   ```

4. **Run Full Backend Test Suite**:
   ```bash
   python -m pytest tests/
   ```

5. **Verify Formatting & Linting**:
   ```bash
   python -m black --check backend/
   python -m ruff check backend/
   ```
