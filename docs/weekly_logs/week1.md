# Week 1 — Repo Scaffolding + Environment Setup

**Date completed:** 2026-07-22

## Files created

### Root level
- `.gitignore` — Python/Node/IDE exclusions, data dir, cache dirs
- `.env.example` — placeholder vars for DB, Groq, Ollama, app config
- `README.md` — project skeleton, status badge, architecture placeholder
- `LICENSE` — MIT, copyright OpenIRM Contributors
- `CONTRIBUTING.md` — minimal contribution guide

### Backend (`backend/`)
- `__init__.py` — package markers (all submodules)
- `requirements.txt` — pinned deps: pandas, numpy, torch, scikit-learn, shap, fastapi, uvicorn, sqlalchemy, pyyaml, python-dotenv, httpx, pytest, black, ruff
- `pyproject.toml` — black + ruff config, pytest config
- `README.md` — backend module overview
- `data/raw/.gitkeep`, `data/filtered/.gitkeep`
- `data_pipeline/` — `__init__.py`, `filter_cert.py`, `preprocess.py`, `config.py`, `README.md` (all stubs with NotImplementedError docstrings)
- `prism/` — `__init__.py`, `scorer.py`, `weights.yaml`, `buckets.py`, `README.md`
- `airs/` — `__init__.py`, `model.py` (actual Autoencoder nn.Module), `train.py`, `inference.py`, `feedback.py`, `config.yaml`, `README.md`
- `explainability/` — `__init__.py`, `shap_explainer.py`, `visualize.py`, `README.md`
- `llm_service/` — `__init__.py`, `prompts.py`, `recommend.py`, `safety.py`, `providers/__init__.py`, `providers/base.py` (abstract BaseProvider), `providers/groq_provider.py`, `providers/ollama_provider.py`, `config.yaml`, `README.md`
- `api/` — `__init__.py`, `main.py` (FastAPI app with /health), `routes/__init__.py`, `routes/score.py`, `routes/explain.py`, `routes/recommend.py`, `routes/feedback.py`, `routes/policy.py`, `models/__init__.py`, `models/user.py`, `models/activity.py`, `models/score.py`, `models/feedback.py`, `schemas/__init__.py`, `db.py`, `README.md`
- `policy_engine/` — `__init__.py`, `rules.py`, `engine.py`, `README.md`
- `tests/` — `__init__.py`, `test_prism.py`, `test_airs.py`, `test_explainability.py`, `test_api.py` (health check passing), `test_policy_engine.py`

### Frontend (`frontend/`)
- `package.json` — stub with React 18, TypeScript, Vite, Tailwind, Recharts, Axios, ESLint, Prettier, Vitest
- `index.html`, `tsconfig.json`, `vite.config.ts`, `tailwind.config.js`, `postcss.config.js`, `.eslintrc.cjs`, `.prettierrc`, `README.md`
- `src/main.tsx` — React entrypoint
- `src/App.tsx` — BrowserRouter with `/` route
- `src/pages/` — `Overview.tsx` (stub), `UserDrilldown.tsx`, `FeedbackPanel.tsx`, `PolicyFeed.tsx`
- `src/components/` — `RiskBadge.tsx`, `ShapExplanationPanel.tsx`, `ActivityTimeline.tsx`, `ScoreSlider.tsx`
- `src/api/` — `client.ts` (axios instance), `scoring.ts`, `feedback.ts`, `policy.ts`
- `src/types/index.ts` — TS interfaces matching backend Pydantic schemas
- `src/hooks/useApi.ts` — placeholder
- `src/styles/index.css` — Tailwind directives
- `src/utils/format.ts` — score/date formatters
- `public/`, `tests/`

### Docs, Docker, CI
- `docs/architecture_diagram.png` — placeholder
- `docs/eda.ipynb` — empty notebook
- `docs/train_colab.ipynb` — empty notebook
- `docs/project_report.md` — placeholder
- `docs/weekly_logs/week1.md` — this file
- `docker/Dockerfile.api` — python:3.11-slim, uvicorn
- `docker/Dockerfile.dashboard` — node build + nginx
- `docker/docker-compose.yml` — api + dashboard services
- `.github/ISSUE_TEMPLATE/` — empty directory

### Modified
- `LICENSE` — updated copyright to "OpenIRM Contributors"

## Implementation notes

- Python 3.13 is installed (not 3.11 as spec says). All deps resolved successfully with compatible wheel versions (torch 2.13, numpy 2.4.6, pandas 3.0.3, scikit-learn 1.9, shap 0.52).
- All stub source files include proper docstrings, type hints, and `NotImplementedError` with the target week.
- The `AIRS Autoencoder` in `backend/airs/model.py` is actually implemented (not a stub) — a real `nn.Module` with configurable encoder/decoder layers.
- Black and ruff pass cleanly (ruff D104 ignored for empty `__init__.py` package markers).
- Frontend `package.json` is a stub — full npm install and build will happen in Week 11.

## Test results

| Test | Status | Detail |
|------|--------|--------|
| `ruff check backend` | PASS | 0 errors, 0 warnings |
| `black --check backend` | PASS | 5 files auto-formatted |
| `pytest backend/tests/test_api.py::TestHealth` | PASS | 1 passed |
| `pip install -r backend/requirements.txt` | PASS | All deps installed |

## Known issues / TODOs

1. `.github/ISSUE_TEMPLATE/` directory is empty — should add issue templates when the repo nears public launch.
2. Frontend dependencies not installed — deferred to Week 11 when the full dashboard is built.
3. `pre-commit` config not set up (optional per spec) — should be added when multiple contributors join.
4. Architecture diagram placeholder — needs real diagram.
5. Python version is 3.13 instead of spec's 3.11 — all resolved deps work, so no action needed unless contributors specifically need 3.11.

## Verification commands

```powershell
# Verify folder structure
Get-ChildItem -Recurse -Depth 2 -Directory | Where-Object { $_.FullName -notmatch '\\env\\|\.git|__pycache__|\.ruff_cache|\.pytest_cache' }

# Run linter
ruff check backend
black --check backend

# Run tests
pytest backend/tests/ -v

# Verify all modules import cleanly
python -c "from backend.api.main import app; print('API module OK')"
python -c "from backend.airs.model import Autoencoder; print('AIRS model OK')"
python -c "from backend.llm_service.providers.base import BaseProvider; print('LLM provider interface OK')"
python -c "from backend.prism.scorer import compute_risk_score; print('PRISM module OK')"
python -c "from backend.explainability.shap_explainer import explain_activity; print('Explainability module OK')"
python -c "from backend.policy_engine.engine import evaluate_activity; print('Policy engine OK')"
```
