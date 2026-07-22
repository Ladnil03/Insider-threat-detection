# OpenIRM — AI-Driven Insider Risk Management

![Status](https://img.shields.io/badge/status-under%20development-yellow)
![License](https://img.shields.io/badge/license-MIT-blue)

**OpenIRM** is an open-source, AI-driven insider risk management (IRM) system
inspired by the paper *"AI-Driven IRM: Transforming Insider Risk Management
with Adaptive Scoring and LLM-Based Threat Detection"* (Koli et al.,
arXiv:2505.03796, May 2025). It combines a rule-based scoring engine (PRISM),
an adaptive autoencoder (AIRS), SHAP-based explainability, and LLM-powered
analyst recommendations into a single, deployable pipeline.

## Key features

- **PRISM scoring** — peer-reviewed rule-based insider risk scoring
- **AIRS autoencoder** — adaptive anomaly detection via reconstruction error
- **SHAP explainability** — per-feature attribution for every risk score
- **LLM recommendations** — Groq-powered (or local Ollama) plain-English analyst notes
- **Policy engine** — automated rule violation detection with audit logging
- **React dashboard** — risk table, user drill-down, SHAP panel, feedback controls

## Architecture

```
Data (CERT CSVs) → PRISM + AIRS → SHAP → LLM → FastAPI → React Dashboard
```

*(Detailed diagram: `docs/architecture_diagram.png`)*

## Status

This project is under active development. See `docs/weekly_logs/` for
progress.

## License

MIT — see `LICENSE`.

## Citation

If you use OpenIRM in your research, please cite the base paper:

```bibtex
@article{koli2025ai,
  title={AI-Driven IRM: Transforming Insider Risk Management with Adaptive
         Scoring and LLM-Based Threat Detection},
  author={Koli, D. and others},
  journal={arXiv preprint arXiv:2505.03796},
  year={2025}
}
```
