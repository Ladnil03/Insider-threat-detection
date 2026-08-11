# Week 4 Completion Log: PRISM (Privilege-based Risk & Insider Scoring Mechanism) Rule Engine

- **Date Completed**: 2026-08-05
- **Author**: Antigravity Assistant & OpenIRM Team

---

## 1. Files Created and Modified

### Backend PRISM Module (`backend/prism/`)
- `backend/prism/weights.yaml`: Configured all 7 category weights ($W_P, W_A, W_C, W_{IP}, W_B, W_D, W_{CA}$), decay factor (0.95), and risk bucket thresholds.
- `backend/prism/buckets.py`: Implemented type-annotated `min_max_normalize` (Min-Max scaling to $[0.0, 1.0]$) and threshold-driven `classify_risk_score` (`LOW`, `MODERATE`, `HIGH`, `CRITICAL`).
- `backend/prism/scorer.py`: Implemented 7 pure, side-effect-free sub-score functions (`user_privilege_score`, `activity_type_score`, `application_context_score`, `ip_score`, `business_hours_score`, `device_compliance_score`, `cumulative_activity_score`), composite `calculate_prism_score` formula calculator, `load_prism_config`, and `score_activity_row` adapter.
- `backend/prism/batch_scorer.py`: Implemented vectorized batch scoring pipeline (`score_dataframe`, `run_batch_scoring`, `main`) over `activity_features.parquet`, exporting `prism_scored_activity.parquet`.
- `backend/prism/README.md`: Updated module documentation with sub-score formulas, weight tuning rationale, worked example details, and CLI commands.

### Backend Test Suite (`backend/tests/`)
- `backend/tests/test_prism.py`: Implemented 11 unit & regression tests covering each sub-score function, Min-Max normalization, risk bucketing, synthetic batch scoring, and the paper's worked example regression test.

### Documentation & Reports (`docs/`)
- `docs/phase_reports/week4_prism_results.md`: Created detailed phase report documenting formula parameters, worked example validation, empirical dataset score distributions, and deliverable metrics.
- `docs/weekly_logs/week4.md`: This completion log.

---

## 2. Implementation Summary

- **Pure Sub-Score Functions**: Built 7 pure, independently testable sub-score functions in `backend/prism/scorer.py` strictly implementing the paper formula $R = (W_P \cdot S_P) + (W_A \cdot S_A) + (W_C \cdot S_C) + (W_{IP} \cdot S_{IP}) + (W_B \cdot S_B) + (W_D \cdot S_D) + (W_{CA} \cdot S_{CA})$.
- **Configurable YAML Weights**: Externalized all weights and thresholds into `backend/prism/weights.yaml` with dynamic loader support.
- **Normalization & Risk Bucketing**: Implemented `min_max_normalize` to clip raw scores to $[0.0, 1.0]$ and `classify_risk_score` to assign `LOW`, `MODERATE`, `HIGH`, or `CRITICAL` risk buckets.
- **Vectorized Batch Scoring**: Developed `backend/prism/batch_scorer.py` to process the 99,987 daily user-activity records from Week 3 and generate `backend/data/filtered/processed/prism_scored_activity.parquet`.
- **Paper Worked Example Regression Test**: Verified that a low-privilege employee, unknown IP, SharePoint, 5 files moved, off-hours, non-compliant device yields a score of `0.3850` (`MODERATE` risk level).
- **Threat Separation Check**: Demonstrated clean score separation on CERT r4.2 dataset: mean score for malicious user-days (`0.6761`) is significantly higher than benign user-days (`0.5730`), placing **82.84%** of malicious user-days into the `HIGH` risk bucket.

---

## 3. Deviations from Original Week 4 Prompt

- None. All 7 pure sub-score functions, YAML configuration, Min-Max normalization, risk bucketing, batch scoring pipeline, paper worked example regression test, phase report, and weekly log match the Week 4 task prompt requirements.

---

## 4. Test Results & Metrics

- **pytest suite**: Passed **31 / 31** tests across all backend modules (0 failures).
  - `tests/test_prism.py`: 11 passed (7 sub-scores, worked example regression, normalization, risk bucketing, synthetic batch scoring)
  - `tests/test_preprocess.py`: 10 passed
  - `tests/test_filter_cert.py`: 4 passed
  - `tests/test_airs.py`: 2 passed
  - `tests/test_api.py`: 2 passed
  - `tests/test_explainability.py`: 1 passed
  - `tests/test_policy_engine.py`: 1 passed
- **Empirical Batch Scoring Metrics**:
  - Total Scored Records: **99,987 user-days**
  - Mean Benign PRISM Score: **0.5730**
  - Mean Malicious PRISM Score: **0.6761**
  - Separation Delta: **+0.1031**
  - Malicious User-Days in High/Critical Bucket: **82.84%** (1,072 / 1,294 user-days)
- **Formatting & Linting**: 100% clean under `black` and `ruff`.

---

## 5. Known Issues / TODOs Carried Forward

- `backend/data/filtered/processed/prism_scored_activity.parquet` will be ingested in Week 5 to train the AIRS autoencoder on benign baseline features and evaluate anomaly reconstruction errors against PRISM risk labels.

---

## 6. Commands to Verify This Week's Work

Run the following commands inside `backend/venv/`:

1. **Run PRISM Unit & Worked Example Regression Tests**:
   ```bash
   python -m pytest tests/test_prism.py -v
   ```

2. **Execute Full Batch Scoring Pipeline**:
   ```bash
   python -m prism.batch_scorer
   ```

3. **Run Complete Backend Test Suite**:
   ```bash
   python -m pytest tests/ -v
   ```

4. **Verify Formatting & Linting**:
   ```bash
   python -m black --check prism/ tests/
   python -m ruff check prism/ tests/
   ```
