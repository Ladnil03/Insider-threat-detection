# OpenIRM — AI-Driven Insider Risk Management System

[![Status: Under Development](https://img.shields.io/badge/Status-Under--Development-orange.svg)](https://github.com/Ladnil03/Insider-threat-detection)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)

**OpenIRM** is an open-source, production-grade Insider Risk Management (IRM) system designed to detect, explain, and mitigate insider threat activity in enterprise environments.

The architecture reproduces and extends the foundational paper:
> **"AI-Driven IRM: Transforming Insider Risk Management with Adaptive Scoring and LLM-Based Threat Detection"**  
> *Koli et al., arXiv:2505.03796 (May 2025)*

OpenIRM combines rule-based scoring (**PRISM**), deep anomaly detection via PyTorch autoencoders (**AIRS**), game-theoretic explainability (**SHAP**), and open-weight LLM reasoning (**Groq API / Ollama**) to provide analysts with transparent, plain-English risk assessments and recommended actions.

---

## Key Features

- **Hybrid Scoring Pipeline**: Rule-based PRISM sub-score engine combined with adaptive PyTorch Autoencoder (AIRS) reconstruction loss.
- **SHAP Feature Attribution**: Novel explainability layer providing exact quantitative feature contributions for every flagged anomaly.
- **LLM Threat Reasoning**: Natural language threat narrative and action recommendations powered by Groq API (serving open-weight models like Llama 3 / DeepSeek-R1) or local Ollama.
- **Analyst Feedback Loop**: Interactive risk score adjustments with human feedback blending and scheduled model retraining.
- **Automated Policy Engine**: Configurable trigger rules that evaluate user risk profiles and log simulated automated mitigation actions.

---

## Architecture Overview

```
Data Layer (CERT r4.2 CSVs → Preprocessing)
   │
   ├──► Scoring Layer 
   │       ├── PRISM (Rule Engine & Baseline Labels)
   │       └── AIRS (PyTorch Autoencoder Anomaly Detection)
   │
   ├──► Explainability Layer (SHAP Feature Attribution on Reconstruction Loss)
   │
   ├──► Reasoning Layer (Groq API / Ollama Open-Weight LLM Recommendation)
   │
   ├──► Service & Policy Layer (FastAPI REST Endpoints & Automated Rule Engine)
   │
   └──► Presentation Layer (React + TypeScript Analyst Dashboard)
```

---

## Local Setup & Quickstart

> [!IMPORTANT]
> **Virtual Environment Requirement**:  
> All Python commands **MUST** be executed inside the virtual environment located at `backend/venv/`. Do not install packages globally.

### 1. Clone Repository
```bash
git clone https://github.com/Ladnil03/Insider-threat-detection.git
cd Insider-threat-detection
```

### 2. Create and Activate Python Virtual Environment

- **Windows (CMD)**:
  ```cmd
  python -m venv backend\venv
  backend\venv\Scripts\activate
  ```

- **Windows (PowerShell)**:
  ```powershell
  python -m venv backend\venv
  backend\venv\Scripts\Activate.ps1
  ```

- **Linux / macOS**:
  ```bash
  python -m venv backend/venv
  source backend/venv/bin/activate
  ```

Upon activation, your shell prompt will show `(venv)`.

### 3. Install Dependencies
Inside the activated virtual environment, run:
```bash
pip install -r backend/requirements.txt
```

### 4. Code Formatting & Linting Check
```bash
black --check backend/
ruff check backend/
```

---

## Project Structure

- `backend/`: FastAPI application, PyTorch AIRS model, PRISM rule engine, SHAP explainer, LLM service, policy engine, and pytest test suite.
- `frontend/`: React + TypeScript frontend dashboard (Vite + Tailwind CSS).
- `docs/`: Architecture diagrams, Jupyter notebooks, phase reports, and weekly completion logs (`docs/weekly_logs/`).
- `docker/`: Docker containerization configs for API and dashboard services.

---

## License

This project is licensed under the [MIT License](LICENSE).
