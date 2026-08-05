# OpenIRM Backend

The backend of **OpenIRM** provides the core risk engine, ML models, explainability pipeline, LLM integration, and FastAPI REST endpoints.

## Directory Overview

- `data/`: Raw and filtered CERT r4.2 dataset storage (gitignored).
- `data_pipeline/`: CERT dataset filter script, feature engineering, and normalization.
- `prism/`: Sub-score calculator (baseline rule engine).
- `airs/`: PyTorch Autoencoder anomaly detection model, training loop, and retraining module.
- `explainability/`: SHAP attribution wrapper for PyTorch reconstruction error explanation.
- `llm_service/`: Modular provider layer for Groq API / Ollama LLM recommendation generation.
- `api/`: FastAPI REST controllers, SQLAlchemy database models, Pydantic schemas.
- `policy_engine/`: Rule evaluation engine for automated risk mitigation triggering.
- `tests/`: Automated unit and integration test suite using `pytest`.

## Virtual Environment Requirement

Always activate `backend/venv/` before running any backend script or test:
```bash
# Windows
backend\venv\Scripts\activate

# Linux / macOS
source backend/venv/bin/activate
```

## Running Tests
```bash
pytest tests/
```
