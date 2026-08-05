# Week 3b Completion Log: Data Preprocessing Retrofit (Feature Engineering & Time Split)

- **Date Completed**: 2026-08-05
- **Author**: Antigravity Assistant & OpenIRM Team

---

## 1. Files Created and Modified

### Backend Data Pipeline (`backend/data_pipeline/`)
- `backend/data_pipeline/config.py`: Added constants for `SPLIT_METADATA_PATH`, base count features (`BASE_FEATURE_COLS`), rolling window definitions (`ROLLING_WINDOWS`), baseline deviation window (`BASELINE_DEVIATION_WINDOW`), and combined feature list (`ALL_FEATURE_COLS`, 72 total features) with insider-threat rationales.
- `backend/data_pipeline/preprocess.py`: Extended pipeline with:
  - `compute_rolling_features()`: Extracts 7-day and 30-day rolling mean & std per user for each activity count feature (48 rolling features).
  - `compute_baseline_deviation_features()`: Extracts 30-day standardized baseline deviation per user (`(today - mean_30d) / std_30d`) using `shift(1)`. Cold-start (history < 30 days) is set to `0.0`, and zero-variance baseline is handled via unit scaling.
  - `split_by_time()`: Sorts by `date_day` and splits into contiguous time windows (`train` 70%, `val` 15%, `test` 15%) enforcing zero date overlap.
  - Updated `build_daily_feature_matrix()`, `save_processed_data()`, and `main()` CLI to compute features, assign `split` tags, and export `split_metadata.json`.
- `backend/data_pipeline/README.md`: Updated module documentation with the 72-feature schema, baseline cold-start handling strategy, time-based split details, and new artifact outputs.

### Dependencies & Tests (`backend/tests/`)
- `backend/tests/test_preprocess.py`: Added unit tests for `compute_rolling_features()`, `compute_baseline_deviation_features()`, `split_by_time()` (verifying zero date overlap), and artifact export including `split_metadata.json`.

### Documentation (`docs/weekly_logs/`)
- `docs/weekly_logs/week3b.md`: Supplementary completion log detailing the retrofit.

---

## 2. Implementation Summary

- **7-Day and 30-Day Rolling Window Features**: Computed per-user 7-day and 30-day rolling means and standard deviations across all 12 base daily activity count features, producing 48 new rolling features that capture acute activity volume spikes (7d) and medium-term behavioral baselines (30d).
- **30-Day Standardized Baseline Deviation**: Implemented per-user 30-day standardized baseline deviation (`(today - mean_30d) / std_30d`) with `shift(1)` to prevent self-contamination. Cold-start periods (fewer than 30 days of trailing history) are explicitly set to `0.0` (neutral deviation). Zero-variance baselines are safely handled using unit scaling (`1.0`) so spikes relative to constant baselines are preserved.
- **Contiguous Time-Based Dataset Split**: Implemented `split_by_time()` to partition the daily user feature matrix into contiguous chronological windows (`train`: 70%, `val`: 15%, `test`: 15%). Added a `split` column to the Parquet dataset and saved exact date boundaries to `backend/data/filtered/processed/split_metadata.json` for downstream AIRS (Week 5) and evaluation (Week 6) reuse.
- **Downstream Audit**: Verified that no downstream modules in `backend/airs/` or `backend/prism/` assume a random row split, ensuring full backward compatibility.

---

## 3. Deviations from Original Week 3 Prompt

- None. All requested retrofit extensions (rolling window features, per-user baseline deviation, cold-start handling, contiguous time-based split with zero date overlap, unit tests, README updates, and supplementary log) were implemented ON TOP of the existing preprocessor without breaking existing functionality.

---

## 4. Test Results & Metrics

- **pytest suite**: Passed **10 / 10** tests in `tests/test_preprocess.py` (0 failures).
- **Full backend pytest suite**: Passed **22 / 22** tests across all backend modules.
- **Feature Extraction Metrics**:
  - Total Daily Features Extracted: **72 features** (12 base counts + 48 rolling mean/std + 12 baseline deviations)
  - Target Label: `is_malicious`
  - Partition Label: `split` (`train`, `val`, `test`)
- **Contiguous Time Split Boundaries**:
  - `split_metadata.json` exported to `backend/data/filtered/processed/split_metadata.json`
- **Formatting & Linting**: 100% clean under `black` and `ruff`.

---

## 5. Known Issues / TODOs Carried Forward

- `backend/data/filtered/processed/activity_features.parquet` now contains all 72 features and the `split` column.
- Week 4 (PRISM Rule Engine) will consume the base features and sub-scores.
- Week 5 (AIRS Autoencoder) will ingest the `train` split of benign activity records using the feature vectors defined in `ALL_FEATURE_COLS`.

---

## 6. Commands to Verify This Week's Work

Run the following commands inside `backend/venv/`:

1. **Run Preprocessing Unit Tests**:
   ```bash
   python -m pytest tests/test_preprocess.py
   ```

2. **Run Full Backend Test Suite**:
   ```bash
   python -m pytest tests/
   ```

3. **Re-run Preprocessing Pipeline CLI**:
   ```bash
   python -m data_pipeline.preprocess
   ```

4. **Verify Formatting & Linting**:
   ```bash
   python -m black --check backend/
   python -m ruff check backend/
   ```
