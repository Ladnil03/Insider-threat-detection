# Week 2 Completion Log: CERT Dataset Filtering (`backend/data_pipeline/filter_cert.py`)

- **Date Completed**: 2026-07-28
- **Author**: Antigravity Assistant & OpenIRM Team

---

## 1. Files Created and Modified

### Data Pipeline Module (`backend/data_pipeline/`)
- `backend/data_pipeline/config.py`: Added constants for raw/filtered paths, column schema selections (`LOGON_USECOLS`, `FILE_USECOLS`, `DEVICE_USECOLS`, `EMAIL_USECOLS`, `WEB_USECOLS`), random seed (42), default benign count (300), and chunk size (100,000).
- `backend/data_pipeline/filter_cert.py`: Implemented malicious metadata parser (`extract_malicious_metadata`), seeded benign user sampler (`sample_benign_users`), memory-efficient chunked CSV filter (`filter_csv_file`), end-to-end pipeline runner (`run_filtering_pipeline`), and CLI argument interface (`main`).
- `backend/data_pipeline/README.md`: Updated with CLI usage examples, parameter descriptions, input/output structures, and memory-saving chunking details.

### Test Suite (`backend/tests/`)
- `backend/tests/test_filter_cert.py`: Created synthetic test suite covering malicious metadata extraction, seeded sampling reproducibility, chunked CSV filtering by user + date bounds, and end-to-end pipeline execution on synthetic temporary datasets.

---

## 2. Implementation Summary

- **Named Constants & Schema Isolation**: Consolidated all paths, raw file names, default seeds, and `usecols` selections into `backend/data_pipeline/config.py`. No magic numbers or hardcoded column lists exist in the processing logic.
- **Memory-Efficient Chunked Subsampling**: Built `filter_csv_file` using `pandas.read_csv(chunksize=100000, usecols=...)`. Ensures raw 20GB+ CERT CSV files are never loaded completely into RAM, preserving system resources.
- **Scenario Date Bounds & Malicious Extraction**: Automatically parses `answers/insiders.csv` to isolate the 30 malicious users and calculate min/max timestamp bounds (6–9 month observation window).
- **Seeded Benign Sampling**: Implemented deterministic benign sampling (`seed=42`) from `psychometric.csv` or logon logs, strictly excluding malicious user IDs.
- **CLI Interface**: Made `filter_cert.py` directly executable via `python -m data_pipeline.filter_cert --benign-users 300 --seed 42` with zero-argument default fallbacks.
- **Synthetic Unit Testing**: Wrote isolated tests in `backend/tests/test_filter_cert.py` using synthetic temporary CSV data, enabling CI and open-source contributors to run tests without requiring the raw 20GB dataset.

---

## 3. Deviations from Original Week 2 Prompt

- None. All tasks, CLI interface options, fallback handling, chunking logic, unit tests, and documentation match the Week 2 prompt requirements.

---

## 4. Test Results & Metrics

- **pytest suite**: Passed **12 / 12** tests (0 failures).
  - `tests/test_filter_cert.py`: 4 passed (synthetic metadata extraction, seeded sampling, chunked CSV filtering, full pipeline execution)
  - `tests/test_prism.py`: 2 passed
  - `tests/test_airs.py`: 2 passed
  - `tests/test_explainability.py`: 1 passed
  - `tests/test_api.py`: 2 passed
  - `tests/test_policy_engine.py`: 1 passed
- **black formatter check**: Clean across all 48 Python source files.
- **ruff linter check**: All checks passed cleanly (0 warnings, 0 errors).

---

## 5. Known Issues / TODOs Carried Forward

- Subsampled CSVs produced by `filter_cert.py` will be consumed in Week 3 to compute daily feature matrices (logon after hours, USB transfer counts, email/web indicators).

---

## 6. Commands to Verify This Week's Work

Run the following commands inside `backend/venv/`:

1. **Test CLI Help Interface**:
   ```bash
   python -m data_pipeline.filter_cert --help
   ```

2. **Run Synthetic Unit Tests**:
   ```bash
   python -m pytest tests/test_filter_cert.py
   ```

3. **Run Complete Backend Test Suite**:
   ```bash
   python -m pytest tests/
   ```

4. **Verify Formatting & Linting**:
   ```bash
   python -m black --check backend/
   python -m ruff check backend/
   ```
