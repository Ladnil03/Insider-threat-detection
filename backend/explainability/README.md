# OpenIRM Explainability Module (`backend/explainability/`)

## 1. Overview & Novel Contribution

A critical limitation of the foundational paper (*"AI-Driven IRM: Transforming Insider Risk Management with Adaptive Scoring and LLM-Based Threat Detection"*, Koli et al., arXiv:2505.03796) is that it leaves **Explainable AI (XAI) as unaddressed future work**. While deep autoencoder reconstruction errors effectively detect multi-dimensional anomalous user activity, black-box anomaly scores provide zero operational context to Security Operations Center (SOC) analysts.

**OpenIRM directly resolves this gap** by introducing a game-theoretic **SHAP (Shapley Additive exPlanations)** layer wrapped around the AIRS Autoencoder's scalar reconstruction error.

---

## 2. Mathematical Foundation & Explainer Rationale

### The Reconstruction Loss Function
The AIRS Autoencoder anomaly score is a composite scalar reconstruction error over $D=72$ user activity metrics:
$$\mathcal{L}_{\text{MSE}}(x) = \frac{1}{D} \sum_{i=1}^{D} \left( x_i - \hat{x}_i \right)^2 \quad \text{where } \hat{x} = \text{Decoder}(\text{Encoder}(x))$$

### Why `shap.KernelExplainer` over `DeepExplainer`
- `DeepExplainer` is designed for feedforward classification logits where linear gradient backpropagation is tractable.
- For autoencoder anomaly detection, our prediction function $f: \mathbb{R}^{72} \to \mathbb{R}$ is the non-linear reconstruction error itself.
- `shap.KernelExplainer` treats $f(x)$ as a black-box scoring function, generating coalitional feature perturbations against a representative benign background baseline ($N=50$) to solve the weighted linear regression game and compute exact Shapley attributions $\phi_i$.

### Efficiency Axiom
Every computed explanation satisfies the Shapley Efficiency Axiom within sampling tolerance ($\epsilon \le 0.15$):
$$\sum_{i=1}^D \phi_i + \text{base\_value} \approx f(x)$$

---

## 3. Module Architecture

```
backend/explainability/
├── __init__.py
├── README.md                   # This architecture documentation
├── shap_explainer.py           # AIRSShapExplainer & explain_activity()
├── visualize.py                # Reusable waterfall and summary plot generators
└── evaluate_explanations.py    # Benchmark evaluation on CERT malicious scenarios
```

---

## 4. Key Functions

### `explain_activity(activity_record, top_k=5, nsamples=150)`
Computes local feature attributions for any single daily user session.
```python
from explainability.shap_explainer import AIRSShapExplainer

explainer = AIRSShapExplainer()
explanation = explainer.explain_activity(user_activity_record, top_k=5)

print(explanation["human_readable_summary"])
# Output: "Primary risk drivers: Mass USB File Exfiltration Spike (30-Day Z-Score): 45.2%, Off-Hours Logons (Night/Weekend): 32.1%"
```

### `generate_waterfall_plot(explanation, output_path=...)`
Generates a publication-grade horizontal waterfall chart showing exact positive and negative feature pushes.

### `generate_summary_plot(shap_matrix, feature_matrix, ...)`
Generates global feature importance ranking across benign and malicious populations.

---

## 5. Verification & Testing

Run unit tests and property checks:
```bash
python -m pytest tests/test_explainability.py -v
```

Generate scenario explanations and visualization artifacts:
```bash
python -m explainability.evaluate_explanations
```
