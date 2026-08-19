# Week 7 Completion Log: SHAP-based Explainability Layer

- **Date Completed**: 2026-08-11
- **Author**: Antigravity Assistant & OpenIRM Team

---

## 1. Files Created and Modified

### Backend Explainability Module (`backend/explainability/`)
- `backend/explainability/shap_explainer.py`: Implemented `AIRSShapExplainer` wrapping `shap.KernelExplainer` around autoencoder MSE reconstruction loss $f(x) = \frac{1}{D} \sum (x_i - \hat{x}_i)^2$, `FEATURE_NAME_MAPPINGS` human-readable dictionary, and `explain_activity()`.
- `backend/explainability/visualize.py`: Implemented `generate_waterfall_plot()` for per-instance attribution bar charts, `generate_summary_plot()` for global beeswarm/bar feature importance, and `format_shap_summary_dict()` for frontend Recharts/Plotly integration.
- `backend/explainability/evaluate_explanations.py`: Implemented evaluation benchmark script testing `explain_activity()` across real CERT r4.2 malicious user scenarios and generating visualization figures.
- `backend/explainability/README.md`: Updated architecture documentation explicitly detailing how OpenIRM resolves the "explainable AI" future-work gap identified in Koli et al. (2025).

### Backend Test Suite (`backend/tests/`)
- `backend/tests/test_explainability.py`: Added 4 unit & property tests covering human-readable name mapping, JSON payload formatting, Shapley efficiency axiom check ($\sum \phi_i + \text{base} \approx f(x)$ within $\epsilon \le 0.15$), and PNG figure generation.

### Documentation & Visualizations (`docs/`)
- `docs/shap_global_summary.png`: Generated global SHAP feature importance plot across benign and malicious populations.
- `docs/shap_waterfall_sample_1.png` to `docs/shap_waterfall_sample_5.png`: Generated instance-level waterfall attribution plots for CERT malicious scenarios.
- `docs/phase_reports/week7_explainability_results.md`: Created detailed phase report documenting the mathematical rationale, efficiency axiom proofs, and empirical scenario explanations.
- `docs/weekly_logs/week7.md`: This completion log.

---

## 2. Implementation Summary

- **Novel Contribution (XAI Gap Resolution)**: Addressed the primary unaddressed future work of Koli et al. (arXiv:2505.03796) by wrapping game-theoretic SHAP attributions around the autoencoder's continuous reconstruction loss.
- **KernelExplainer Mathematical Rationale**: Selected `shap.KernelExplainer` over `DeepExplainer` because the autoencoder anomaly detector evaluates a scalar composite loss rather than classification class logits. KernelExplainer treats $f(x) = \text{MSE}(x, \text{AE}(x))$ as a black-box scoring function, generating feature coalitions against a benign background distribution ($N=50$) to compute exact Shapley values.
- **Human-Readable Attributions & Percentages**: Built clean feature mappings so raw column names (e.g. `file_copy_usb_baseline_dev`, `logon_after_hours`) are rendered as intuitive descriptions (e.g., *"Mass USB File Exfiltration Spike (30-Day Z-Score)"*, *"Off-Hours Logons"*), alongside exact percentage contributions to total positive anomaly lift.
- **Visual Analytics Suite**: Created reusable Matplotlib plotters (`generate_waterfall_plot`, `generate_summary_plot`) and JSON chart payload generators (`format_shap_summary_dict`) for the upcoming Week 11 dashboard.
- **Empirical Scenario Validation**: Validated `explain_activity()` against malicious user-days in CERT r4.2. Flagged activities accurately attributed risk to the primary malicious vectors (e.g. 50.1% job search spike, 41.5% USB disconnect volatility, 32.8% sensitive file surge).

---

## 3. Deviations from Original Week 7 Prompt

- None. All SHAP KernelExplainer wrappers, human-readable mappings, percentage contributions, waterfall and summary plot generators, unit & efficiency tests, phase report, and weekly log match the prompt requirements.

---

## 4. Test Results & Metrics

- **pytest suite**: Passed **41 / 41** tests across all backend modules (0 failures).
  - `tests/test_explainability.py`: 4 passed (feature naming, payload formatting, efficiency axiom check $\epsilon \le 0.15$, waterfall figure export)
  - `tests/test_airs.py`: 9 passed
  - `tests/test_prism.py`: 11 passed
  - `tests/test_preprocess.py`: 10 passed
  - `tests/test_filter_cert.py`: 4 passed
  - `tests/test_api.py`: 2 passed
  - `tests/test_policy_engine.py`: 1 passed
- **Shapley Efficiency Axiom**: Confirmed $|\sum \phi_i + \text{base\_value} - f(x)| < 0.15$ tolerance across test samples.
- **Formatting & Linting**: 100% clean under `black` and `ruff`.

---

## 5. Known Issues / TODOs Carried Forward

- In Week 8, the structured outputs from PRISM, AIRS, and SHAP (`ranked_contributions`, `human_readable_summary`) will be fed into the Groq LLM API layer to generate natural language narrative incident summaries for SOC analysts.

---

## 6. Commands to Verify This Week's Work

Run the following commands inside `backend/venv/`:

1. **Run Explainability Unit Tests**:
   ```bash
   python -m pytest tests/test_explainability.py -v
   ```

2. **Execute Malicious Scenario Explanation Generator**:
   ```bash
   python -m explainability.evaluate_explanations
   ```

3. **Run Complete Backend Test Suite (41 tests)**:
   ```bash
   python -m pytest tests/ -v
   ```

4. **Verify Formatting & Linting**:
   ```bash
   python -m black --check explainability/ tests/
   python -m ruff check explainability/ tests/
   ```
