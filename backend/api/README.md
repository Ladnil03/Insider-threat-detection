# OpenIRM REST API Service Layer (`backend/api/`)

## 1. Overview & Architecture

The API module serves as the central operational backbone of OpenIRM, exposing high-performance RESTful endpoints that integrate:
- **Rule-based risk scoring** (PRISM)
- **Semi-supervised autoencoder anomaly detection** (AIRS)
- **Ensemble risk aggregation**
- **Game-theoretic explainability** (SHAP with sub-millisecond caching)
- **Cloud LLM reasoning & recommendations** (Groq open-weight models)
- **Automated enterprise policy rule evaluation**
- **Longitudinal database persistence & analyst feedback blending**

---

## 2. API Endpoints Specification

All endpoints are versioned under `/api/v1` and accessible with interactive Swagger UI at `http://localhost:8000/docs`.

| Method | Endpoint | Description | Request Payload | Response Schema |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/health` | Service health status check | — | `{ status, system, version }` |
| `POST` | `/api/v1/score` | Calculates PRISM, AIRS, & Ensemble score, records activity | `ScoreRequest` | `ScoreResponse` |
| `GET` | `/api/v1/explain/{activity_id}` | Returns SHAP feature attribution breakdown | `top_k` query param | `ExplainResponse` |
| `GET` | `/api/v1/recommend/{activity_id}` | Generates Groq LLM plain-English threat summary & advice | — | `RecommendationResponse` |
| `POST` | `/api/v1/feedback` | Ingests analyst score adjustment and blends adaptive score | `FeedbackCreateRequest` | `FeedbackResponse` |
| `GET` | `/api/v1/policy-violations` | Retrieves audit log of triggered security policy actions | `limit`, `severity` query | `List[PolicyViolationResponse]` |
| `GET` | `/api/v1/users` | Directory of monitored employees & latest risk levels | — | `List[UserSummaryResponse]` |
| `GET` | `/api/v1/users/{user_id}/history` | Longitudinal timeline of activity, scores, and policy flags | — | `UserHistoryResponse` |

---

## 3. Database Schema (`backend/api/models/`)

The storage layer uses SQLAlchemy with automatic SQLite local development support (`sqlite:///./openirm.db`) and zero-code migration compatibility for production PostgreSQL (e.g. Neon / Supabase):

```
+-------------------------------------------------------------------------------+
|                               DATABASE SCHEMA                                 |
+-------------------------------------------------------------------------------+
  [users]
    ├── user_id (PK, String)
    ├── user_name (String)
    ├── role (String)
    └── department (String)
         │
         ├──< [activities]
         │      ├── id (PK, Integer)
         │      ├── user_id (FK -> users.user_id)
         │      ├── date_day (String)
         │      ├── metrics_json (Text)
         │      └── created_at (DateTime)
         │           │
         │           ├──< [scores]
         │           │      ├── id (PK, Integer)
         │           │      ├── activity_id (FK -> activities.id)
         │           │      ├── prism_score (Float)
         │           │      ├── airs_score (Float)
         │           │      ├── ensemble_score (Float)
         │           │      └── risk_level (String)
         │           │
         │           ├──< [feedback]
         │           │      ├── id (PK, Integer)
         │           │      ├── original_score (Float)
         │           │      ├── adjusted_score (Float)
         │           │      └── blended_score (Float)
         │           │
         │           └──< [policy_violations]
         │                  ├── id (PK, Integer)
         │                  ├── rule_id (String)
         │                  ├── severity (String)
         │                  └── action (String)
```

---

## 4. Running the API Server

Start the local development server:
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Access interactive documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 5. Verification & Testing

Execute integration test suite:
```bash
python -m pytest tests/test_api.py -v
```
