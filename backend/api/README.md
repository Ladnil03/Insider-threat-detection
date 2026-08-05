# API Service Module

FastAPI application delivering REST endpoints for scoring, explainability, LLM recommendation, feedback collection, and policy rule status.

## Endpoints

- `POST /api/v1/score`: Computes PRISM, AIRS, and composite risk scores.
- `POST /api/v1/explain`: Computes SHAP feature attribution breakdown.
- `POST /api/v1/recommend`: Calls active LLM provider (Groq/Ollama) to generate natural language analysis.
- `POST /api/v1/feedback`: Accepts analyst score overrides for model blending and retraining.
- `GET /api/v1/policy-violations`: Returns simulated automated mitigation logs.
- `GET /health`: System status health check.

## Inputs / Outputs
Uses Pydantic schemas for request validation and response serialization.
