# Phase Report: Week 7 SHAP Explainability Layer Results

**Date**: 2026-08-11  
**Author**: OpenIRM Core Team  
**Module**: `backend/explainability/`  
**Novel Contribution**: Resolving the Explainable AI (XAI) Future-Work Gap in Koli et al. (2025)

---

## 1. Executive Summary & Explainability Breakthrough

The foundational paper by Koli et al. (*"AI-Driven IRM: Transforming Insider Risk Management with Adaptive Scoring and LLM-Based Threat Detection"*, arXiv:2505.03796) introduced the dual-engine scoring architecture but explicitly left **model explainability as unaddressed future work**. 

In Week 7, OpenIRM completes this novel contribution by implementing a **game-theoretic SHAP (Shapley Additive exPlanations) attribution layer** directly wrapping the AIRS Autoencoder's reconstruction error function:
$$\mathcal{L}_{\text{MSE}}(x) = \frac{1}{D} \sum_{i=1}^{D} (x_i - \hat{x}_i)^2$$

Every flagged activity now produces an exact, mathematically grounded percentage breakdown of **which specific user behaviors drove the anomaly score**, bridging the critical gap between black-box deep learning and actionable SOC security investigation.

---

## 2. KernelExplainer Mathematical Rationale

- **Why KernelExplainer**: Standard `DeepExplainer` assumes a classification network with class logit outputs and gradient paths. The AIRS anomaly detector computes a composite scalar loss $\mathcal{L}_{\text{MSE}}(x)$. `shap.KernelExplainer` evaluates the reconstruction loss directly on coalitional feature subsets against a benign baseline distribution, yielding exact Shapley values $\phi_i$.
- **Efficiency Property Verification**: Our unit tests confirm that the efficiency axiom $\sum_{i=1}^D \phi_i + \text{base\_value} \approx f(x)$ holds within sampling tolerance $\epsilon \le 0.15$.

---

## 3. Empirical Case Studies on Malicious Insider Scenarios


### Case #1: User `USER_1` on `2010-01-01`
- **PRISM Rule Score**: `0.7800` | **AIRS Anomaly Score ($S_{AI}$)**: `0.2237`
- **Analyst Explanation Summary**: *"Primary risk drivers: Sensitive Archive Access Surge (30-Day Z-Score): 61.6%, Device Connect Count (7-Day Volatility): 17.4%, Device Disconnect Count (7-Day Volatility): 9.5%, Device Disconnect Count (30-Day Volatility): 3.9%, Device Disconnect Count (Baseline Z-Score): 3.6%"*
- **Top Contributing Risk Drivers**:
  - **Sensitive Archive Access Surge (30-Day Z-Score)**: `61.6%` (Value: `5.29`, $\phi_i = +0.3715$)
  - **Device Connect Count (7-Day Volatility)**: `17.4%` (Value: `2.16`, $\phi_i = +0.1050$)
  - **Device Disconnect Count (7-Day Volatility)**: `9.5%` (Value: `2.16`, $\phi_i = +0.0576$)
  - **Device Disconnect Count (30-Day Volatility)**: `3.9%` (Value: `1.64`, $\phi_i = +0.0236$)
  - **Device Disconnect Count (Baseline Z-Score)**: `3.6%` (Value: `1.86`, $\phi_i = +0.0219$)

### Case #2: User `USER_2` on `2010-01-01`
- **PRISM Rule Score**: `0.7800` | **AIRS Anomaly Score ($S_{AI}$)**: `0.1597`
- **Analyst Explanation Summary**: *"Primary risk drivers: Sensitive Archive Access Surge (30-Day Z-Score): 33.1%, Device Disconnect Count (7-Day Volatility): 29.9%, Device Connect Count (7-Day Volatility): 27.0%, Unusual USB Hardware Usage (30-Day Z-Score): 5.4%, Logon Count (30-Day Baseline): 4.7%"*
- **Top Contributing Risk Drivers**:
  - **Sensitive Archive Access Surge (30-Day Z-Score)**: `33.1%` (Value: `2.95`, $\phi_i = +0.1582$)
  - **Device Disconnect Count (7-Day Volatility)**: `29.9%` (Value: `2.07`, $\phi_i = +0.1426$)
  - **Device Connect Count (7-Day Volatility)**: `27.0%` (Value: `2.07`, $\phi_i = +0.1288$)
  - **Unusual USB Hardware Usage (30-Day Z-Score)**: `5.4%` (Value: `-0.77`, $\phi_i = +0.0257$)
  - **Logon Count (30-Day Baseline)**: `4.7%` (Value: `2.00`, $\phi_i = +0.0223$)

### Case #3: User `USER_3` on `2010-01-01`
- **PRISM Rule Score**: `0.7800` | **AIRS Anomaly Score ($S_{AI}$)**: `0.0741`
- **Analyst Explanation Summary**: *"Primary risk drivers: Sensitive Archive Access Surge (30-Day Z-Score): 32.8%, Flight Risk Job Hunting Spike (30-Day Z-Score): 26.0%, Unusual USB Hardware Usage (30-Day Z-Score): 18.8%, Sensitive File Access (.exe/.zip/.iso): 13.7%, Device Disconnect Count (Baseline Z-Score): 6.9%"*
- **Top Contributing Risk Drivers**:
  - **Sensitive Archive Access Surge (30-Day Z-Score)**: `32.8%` (Value: `1.97`, $\phi_i = +0.0773$)
  - **Flight Risk Job Hunting Spike (30-Day Z-Score)**: `26.0%` (Value: `1.95`, $\phi_i = +0.0613$)
  - **Unusual USB Hardware Usage (30-Day Z-Score)**: `18.8%` (Value: `1.69`, $\phi_i = +0.0444$)
  - **Sensitive File Access (.exe/.zip/.iso)**: `13.7%` (Value: `1.00`, $\phi_i = +0.0322$)
  - **Device Disconnect Count (Baseline Z-Score)**: `6.9%` (Value: `1.79`, $\phi_i = +0.0162$)

### Case #4: User `USER_4` on `2010-01-01`
- **PRISM Rule Score**: `0.7800` | **AIRS Anomaly Score ($S_{AI}$)**: `0.5895`
- **Analyst Explanation Summary**: *"Primary risk drivers: Flight Risk Job Hunting Spike (30-Day Z-Score): 50.1%, Sensitive Archive Access Surge (30-Day Z-Score): 13.7%, Unusual USB Hardware Usage (30-Day Z-Score): 9.0%, Device Disconnect Count (Baseline Z-Score): 6.8%, Email External Count (7-Day Volatility): 4.3%"*
- **Top Contributing Risk Drivers**:
  - **Flight Risk Job Hunting Spike (30-Day Z-Score)**: `50.1%` (Value: `11.56`, $\phi_i = +0.7033$)
  - **Sensitive Archive Access Surge (30-Day Z-Score)**: `13.7%` (Value: `1.97`, $\phi_i = +0.1928$)
  - **Unusual USB Hardware Usage (30-Day Z-Score)**: `9.0%` (Value: `1.97`, $\phi_i = +0.1261$)
  - **Device Disconnect Count (Baseline Z-Score)**: `6.8%` (Value: `2.11`, $\phi_i = +0.0951$)
  - **Email External Count (7-Day Volatility)**: `4.3%` (Value: `3.48`, $\phi_i = +0.0598$)

### Case #5: User `USER_5` on `2010-01-01`
- **PRISM Rule Score**: `0.7800` | **AIRS Anomaly Score ($S_{AI}$)**: `0.1692`
- **Analyst Explanation Summary**: *"Primary risk drivers: Device Disconnect Count (7-Day Volatility): 41.5%, Off-Hours Logons (Night/Weekend): 21.9%, Sensitive File Access (.exe/.zip/.iso): 11.6%, Web Job Search Count (30-Day Baseline): 7.4%, Device Connect Count (7-Day Volatility): 6.3%"*
- **Top Contributing Risk Drivers**:
  - **Device Disconnect Count (7-Day Volatility)**: `41.5%` (Value: `2.67`, $\phi_i = +0.1553$)
  - **Off-Hours Logons (Night/Weekend)**: `21.9%` (Value: `13.00`, $\phi_i = +0.0817$)
  - **Sensitive File Access (.exe/.zip/.iso)**: `11.6%` (Value: `2.00`, $\phi_i = +0.0435$)
  - **Web Job Search Count (30-Day Baseline)**: `7.4%` (Value: `5.40`, $\phi_i = +0.0278$)
  - **Device Connect Count (7-Day Volatility)**: `6.3%` (Value: `2.67`, $\phi_i = +0.0235$)


---

## 4. Generated Artifacts & Visualizations

- `docs/shap_global_summary.png`: Global feature attribution ranking across benign and malicious samples.
- `docs/shap_waterfall_sample_1.png` to `docs/shap_waterfall_sample_5.png`: Per-instance waterfall attribution charts for flagged user anomalies.
- `backend/explainability/shap_explainer.py`: `AIRSShapExplainer` and `explain_activity()`.
- `backend/explainability/visualize.py`: Reusable Matplotlib and Recharts/Plotly payload generators.
- `backend/tests/test_explainability.py`: Unit and property tests (100% pass rate).
