# AI-Driven IRM (Open Source Edition) — Master Build Prompt (Week-Wise)

**How to use this file:** Paste the "Global Context" block once at the start of a new AI coding assistant session (Claude Code, Cursor, etc.). Then paste ONE week's prompt at a time, in order. Don't let the assistant skip ahead — each week has a deliverable check; confirm it before moving on.

---

## GLOBAL CONTEXT (paste this once, at the start of every new session)

```
You are helping me build an open-source MVP called "OpenIRM" — an AI-driven 
Insider Risk Management system, based on and extending the paper "AI-Driven 
IRM: Transforming Insider Risk Management with Adaptive Scoring and LLM-Based 
Threat Detection" (Koli et al., arXiv:2505.03796, May 2025).

PROJECT GOAL
A working, open-source, resume-quality MVP that:
1. Scores insider risk using a rule-based engine (PRISM) AND an adaptive 
   autoencoder model (AIRS), reproducing the paper's approach.
2. Adds SHAP-based explainability on top of the autoencoder's risk score — 
   this is our novel contribution, since the original paper leaves 
   explainability as unaddressed future work.
3. Uses Groq's free-tier API (serving open-weight models like Llama 3 or 
   DeepSeek-R1 distills) to turn risk score + SHAP explanation into a 
   plain-English analyst recommendation — used for both local dev and the 
   deployed demo, so the LLM layer behaves identically everywhere.
4. Ships as a documented, MIT-licensed, contributor-friendly open-source repo.

CONSTRAINTS (must follow throughout)
- FREE TIER ONLY. No paid APIs, no paid cloud compute, no paid databases. 
  Everything must run on: local machine OR free tiers of GitHub, Google 
  Colab, Hugging Face Spaces, Vercel/Netlify, Neon/Supabase free 
  Postgres tier, Render free tier, Groq free API tier.
- LLM inference uses Groq's free API tier as the sole provider, calling 
  open-weight models (Llama 3.3 70B or DeepSeek-R1 distills, depending on 
  what performs best in testing — decide in Week 9). This is a genuinely 
  free service serving open-weight models, not a paid proprietary API, so 
  it satisfies the open-source/free-tier constraint. Since Groq is a 
  hosted API, be explicit in the README's Limitations section that this 
  trades away the original paper's "on-prem, data-never-leaves-the-system" 
  design for speed and deployment simplicity — the LLM call must still go 
  through a clean provider interface (backend/llm_service/providers/) so a 
  contributor could swap in a local Ollama provider later without touching 
  the rest of the pipeline.
- Dataset: CERT Insider Threat Dataset r4.2, filtered to a 250–350 benign 
  user / all 30 malicious user subset, over a 6–9 month window (I will 
  provide the filtered CSVs — do not assume the full 20GB dataset is loaded 
  into memory at once; always use chunked reads if touching raw files).
- Do not silently skip steps or use placeholder/fake data — if something 
  can't be done with free-tier resources, tell me and propose an alternative 
  rather than pretending it's done.
- After each week, produce: working code, a short README section for that 
  module, and a list of what still needs manual verification from me.

CODE QUALITY RULES (non-negotiable, apply to every line of code written)
- Modular by design: one responsibility per file, one concern per function. 
  If a function is doing more than one logical thing, split it.
- Every function/class has a docstring: what it does, params, return value. 
  Assume the reader is an open-source contributor with zero prior context.
- Type hints on all function signatures (Python: use `typing`; TypeScript: 
  no `any` unless truly unavoidable, and comment why).
- No hardcoded values — magic numbers/thresholds/weights/paths go in config 
  files (YAML/.env), never inline in logic.
- No God files. If a file exceeds ~300 lines, propose how to split it 
  before continuing to add to it.
- Consistent naming: snake_case for Python, camelCase for TS/JS, no mixing.
- Every backend module has a corresponding test file in backend/tests/, mirroring 
  the backend source folder structure.
- Errors are handled explicitly and logged with context — no bare 
  except/catch blocks that swallow errors silently.
- Use dependency injection / config objects over global state, so modules 
  can be tested in isolation.
- Every module folder gets its own short README.md explaining its purpose, 
  inputs, outputs, and how to run/test it standalone.
- Follow PEP8 (Python) and run a linter/formatter (black + ruff for Python, 
  eslint + prettier for the React/TS frontend) — set these up in Week 1 
  and run them before every commit.
- React components: functional components + hooks only (no class 
  components), one component per file, keep components small and focused 
  (split into subcomponents rather than growing one large JSX tree), keep 
  API-calling logic out of components (use the api/ and hooks/ layers), 
  and type all props explicitly with TS interfaces.
- Commit messages follow Conventional Commits (feat:, fix:, docs:, test:, 
  refactor:) so history stays readable for contributors.
- Before writing new code, check if similar logic already exists elsewhere 
  in the repo and reuse/extend it rather than duplicating.

WEEKLY LOG REQUIREMENT (grounding mechanism — non-negotiable)
At the END of every week's work, before considering that week done, you 
must create docs/weekly_logs/weekN.md (N = the week number) containing:
1. Date completed
2. Exact list of files created/modified this week (with paths)
3. What was implemented, in plain terms (2-5 bullet points per module 
   touched)
4. Any deviation from the original week's task prompt, and why
5. Test results: what was tested, pass/fail status, actual metrics/numbers 
   if applicable (e.g. real FPR/TPR values, not estimates)
6. Known issues / TODOs explicitly carried forward to future weeks
7. Exact commands I need to run to verify this week's work myself

At the START of every new session (before doing any new work), you must:
1. Ask me which week we're starting, if not already told
2. Request and read ALL previous docs/weekly_logs/weekN.md files (weeks 1 
   through N-1) before writing any new code — do not rely on memory of 
   earlier conversation turns, since a new session has no access to that 
   history
3. If a previous week's log is missing, incomplete, or its stated file 
   paths don't match what's actually in the repo, STOP and flag this to me 
   instead of guessing or assuming what was built — ask me to paste the 
   log or confirm the repo state first
4. Treat the weekly logs as the single source of truth for "what already 
   exists" — never assume a module/function/file exists just because an 
   earlier week's prompt asked for it; verify against the log and the 
   actual repo (view the relevant files) before building on top of it

TECH STACK (fixed — do not substitute without asking)
- Language: Python 3.11 (backend/ML), TypeScript + React (frontend)
- Data processing: pandas, NumPy
- ML: PyTorch (autoencoder), scikit-learn (baseline/metrics)
- Explainability: SHAP
- LLM: Groq API (free tier) as primary provider, serving open-weight 
  models (llama-3.1-8b-instant or deepseek-r1-distill-llama-70b — pick 
  based on quality/speed tradeoff during Week 9 testing); Ollama as a 
  secondary local/on-prem provider behind the same interface, for fully 
  offline/local development and to preserve the "on-prem" data-sovereignty 
  story from the original paper
- Backend API: FastAPI
- Database: SQLite for local dev, PostgreSQL (Neon/Supabase free tier) for 
  deployed demo
- Frontend: React + TypeScript, Vite (build tool), Tailwind CSS (styling), 
  Recharts (charts/graphs), Axios or fetch for API calls
- Containerization: Docker + docker-compose
- Version control: Git/GitHub, MIT license, Conventional Commits format
- Environment: Dependencies are installed directly into the local Python environment (no project virtual environment folder required)

PROJECT STRUCTURE (scaffold this exactly in Week 1, fill in over time)
openirm/
├── backend/
│   ├── data/                          # raw + filtered CSVs (gitignored)
│   │   ├── raw/
│   │   └── filtered/
│   ├── data_pipeline/
│   │   ├── __init__.py
│   │   ├── filter_cert.py             # subsamples CERT dataset
│   │   ├── preprocess.py              # cleaning, joins, normalization
│   │   ├── config.py                  # column lists, paths, constants
│   │   └── README.md
│   ├── prism/
│   │   ├── __init__.py
│   │   ├── scorer.py                  # sub-score functions + weighted total
│   │   ├── weights.yaml                # configurable weights, not hardcoded
│   │   ├── buckets.py                  # risk bucketing thresholds
│   │   └── README.md
│   ├── airs/
│   │   ├── __init__.py
│   │   ├── model.py                    # autoencoder architecture
│   │   ├── train.py                    # training loop
│   │   ├── inference.py                # scoring new activity
│   │   ├── feedback.py                 # human feedback blending + retraining
│   │   ├── config.yaml                 # hyperparams, alpha, retrain threshold
│   │   └── README.md
│   ├── explainability/
│   │   ├── __init__.py
│   │   ├── shap_explainer.py           # SHAP wrapper functions
│   │   ├── visualize.py                # summary/force plot helpers
│   │   └── README.md
│   ├── llm_service/
│   │   ├── __init__.py
│   │   ├── prompts.py                  # prompt templates, kept separate from logic
│   │   ├── recommend.py                # orchestrates: builds prompt, calls
│   │   │                                # active provider, parses response
│   │   ├── safety.py                   # input sanitization before prompting
│   │   ├── providers/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                  # abstract provider interface
│   │   │   ├── groq_provider.py         # Groq API implementation (default)
│   │   │   └── ollama_provider.py       # local Ollama implementation
│   │   ├── config.yaml                  # active provider, model name, API 
│   │   │                                 # key env var name, timeouts
│   │   └── README.md
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py                     # FastAPI app entrypoint
│   │   ├── routes/
│   │   │   ├── score.py
│   │   │   ├── explain.py
│   │   │   ├── recommend.py
│   │   │   ├── feedback.py
│   │   │   └── policy.py
│   │   ├── models/                     # SQLAlchemy ORM models
│   │   │   ├── user.py
│   │   │   ├── activity.py
│   │   │   ├── score.py
│   │   │   └── feedback.py
│   │   ├── schemas/                    # Pydantic request/response schemas
│   │   ├── db.py                       # DB session/engine setup
│   │   └── README.md
│   ├── policy_engine/
│   │   ├── __init__.py
│   │   ├── rules.py                    # policy rule definitions
│   │   ├── engine.py                   # trigger evaluation logic
│   │   └── README.md
│   ├── tests/
│   │   ├── test_prism.py
│   │   ├── test_airs.py
│   │   ├── test_explainability.py
│   │   ├── test_api.py
│   │   └── test_policy_engine.py
│   ├── requirements.txt
│   ├── pyproject.toml                  # black/ruff config
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── main.tsx                 # React entrypoint
│   │   ├── App.tsx                  # top-level routing/layout
│   │   ├── pages/
│   │   │   ├── Overview.tsx
│   │   │   ├── UserDrilldown.tsx
│   │   │   ├── FeedbackPanel.tsx
│   │   │   └── PolicyFeed.tsx
│   │   ├── components/              # reusable UI pieces (cards, tables,
│   │   │   │                        # charts, sliders, badges, etc.)
│   │   │   ├── RiskBadge.tsx
│   │   │   ├── ShapExplanationPanel.tsx
│   │   │   ├── ActivityTimeline.tsx
│   │   │   └── ScoreSlider.tsx
│   │   ├── api/
│   │   │   ├── client.ts            # axios instance + base config
│   │   │   ├── scoring.ts           # /score, /explain, /recommend calls
│   │   │   ├── feedback.ts          # /feedback calls
│   │   │   └── policy.ts            # /policy-violations calls
│   │   ├── types/                   # shared TS interfaces/types, mirroring
│   │   │   └── index.ts             # backend Pydantic schemas
│   │   ├── hooks/                   # custom React hooks (data fetching, etc.)
│   │   ├── styles/
│   │   └── utils/
│   ├── public/
│   ├── tests/                       # Vitest + React Testing Library
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── .eslintrc.cjs
│   ├── .prettierrc
│   └── README.md
├── docs/
│   ├── architecture_diagram.png
│   ├── eda.ipynb
│   ├── train_colab.ipynb
│   ├── project_report.md
│   ├── phase_reports/
│   └── weekly_logs/                # week1.md, week2.md, ... week13.md
│                                    # written at the end of each week —
│                                    # source of truth for what exists
├── docker/
│   ├── Dockerfile.api
│   ├── Dockerfile.dashboard
│   └── docker-compose.yml
├── .github/
│   └── ISSUE_TEMPLATE/
├── .gitignore
├── .env.example
├── README.md
├── CONTRIBUTING.md
└── LICENSE

SYSTEM ARCHITECTURE (reference — build toward this incrementally)
Data Layer (CERT CSVs → pandas preprocessing) 
  → Scoring Layer (PRISM rule engine → labels → AIRS autoencoder → risk score) 
  → Explainability Layer (SHAP per-feature attribution on AIRS output) 
  → Reasoning Layer (Groq API: score + SHAP + user history → recommendation) 
  → Service Layer (FastAPI: /score, /explain, /recommend, /feedback endpoints 
    + policy engine that logs simulated automated actions) 
  → Storage Layer (SQLite/Postgres: users, activities, scores, feedback, policy_violations) 
  → Presentation Layer (React dashboard: risk table, user drill-down, 
    SHAP panel, LLM recommendation panel, feedback slider)

WORKFLOW (what the finished system does end to end)
1. Ingest filtered CERT CSVs → normalize/join on user+timestamp
2. PRISM computes rule-based risk score per activity (baseline + training labels)
3. AIRS autoencoder trains on benign activity, scores new activity via 
   reconstruction error
4. SHAP explains each AIRS score by feature contribution
5. LLM converts (score + SHAP + context) into a recommendation
6. Analyst can adjust score via dashboard slider → feedback stored → 
   periodic retraining
7. Policy engine independently flags rule violations and logs a simulated 
   automated action
8. Dashboard displays all of the above

Confirm you understand this context and the project structure, then wait 
for me to paste the specific week's prompt below.
```

---

## WEEK 1 — Repo Scaffolding + Environment Setup

```
WEEK 1 TASK: Project scaffolding, tooling, and environment

1. Create the exact folder/file structure given in the Global Context 
   "PROJECT STRUCTURE" section (separated into backend/ and frontend/). Every folder gets an empty (or stub) 
   README.md immediately, even before code exists in it — this establishes 
   the modular discipline from day one.

2. Set up tooling:
   - backend/requirements.txt (pinned versions, backend dependencies): pandas, numpy, 
     torch, scikit-learn, shap, fastapi, uvicorn, sqlalchemy, pyyaml, 
     pytest, black, ruff, python-dotenv
   - backend/pyproject.toml with black + ruff config
   - frontend/package.json (set up here as a stub with a placeholder 
     script; full scaffold happens in Week 11): react, react-dom, 
     typescript, vite, tailwindcss, recharts, axios, react-router-dom, 
     eslint, prettier, vitest, @testing-library/react
   - .gitignore (exclude backend/data/, .env, __pycache__, *.pyc, 
     checkpoints/, node_modules/, dist/)
   - .env.example with placeholder vars (DB_URL, OLLAMA_HOST, etc.)
   - pre-commit config (optional but recommended) running black + ruff on 
     every commit

3. Dependencies are installed directly into virtual environment (`pip install -r backend/requirements.txt`).Virtual environment (env) in backend folder.

4. Write the root README.md skeleton: project title, one-paragraph 
   description referencing the base paper, "Status: Under Development" 
   badge, planned architecture diagram placeholder, license badge.

5. Write LICENSE (MIT) and a minimal CONTRIBUTING.md stub (to be expanded 
   in the final week).

6. Initialize git, make the first commit (`chore: initial project scaffold`), 
   push to a new GitHub repo.

DELIVERABLE CHECK: `git clone` the repo fresh, `pip install -r 
backend/requirements.txt`, confirm no errors, confirm folder structure matches the 
spec exactly (with backend/ and frontend/ folders), confirm black/ruff run cleanly on the (empty) codebase.

Before ending this week: write docs/weekly_logs/weekN.md (replace N with this week's number) following the WEEKLY LOG REQUIREMENT format from the Global Context.
```

---

## WEEK 2 — Data Filtering Script

```
WEEK 2 TASK: CERT dataset filtering (backend/data_pipeline/filter_cert.py)

1. Write backend/data_pipeline/config.py: paths to raw data, output paths, column 
   lists to keep per file, random seed (42), target benign user count 
   (300), target date window logic — all as named constants, nothing 
   hardcoded elsewhere.

2. Write backend/data_pipeline/filter_cert.py:
   - Read the CERT r4.2 answers/insiders file → extract the 30 malicious 
     user IDs and their scenario date ranges
   - Compute the union of those date ranges → determine minimum required 
     time window (6-9 months)
   - Randomly sample 250-350 benign users from users.csv (seeded)
   - Chunk-read logon.csv, file.csv, device.csv (chunksize=100000, 
     usecols=config-defined columns only) filtered to selected users + 
     date window
   - Write slim output CSVs to backend/data/filtered/
   - Log a summary: total rows, users, date range, class balance, output 
     file sizes

3. Keep the script CLI-runnable: `python -m backend.data_pipeline.filter_cert 
   --benign-users 300 --seed 42` with sensible defaults so it also runs 
   with zero args.

4. Write backend/tests/test_filter_cert.py using a tiny synthetic mock CSV (not the 
   real dataset) to verify the filtering logic works correctly in 
   isolation — this is important for CI and for contributors who don't 
   have the real dataset.

5. Update backend/data_pipeline/README.md: what this script does, how to run it, 
   expected output.

DELIVERABLE CHECK: Running the script on the real dataset produces slim 
CSVs in backend/data/filtered/ totaling roughly 2-4GB, containing all 30 malicious 
users fully within their scenario windows, plus the benign sample.

Before ending this week: write docs/weekly_logs/weekN.md (replace N with this week's number) following the WEEKLY LOG REQUIREMENT format from the Global Context.
```

---

## WEEK 3 — Preprocessing + EDA

```
WEEK 3 TASK: Preprocessing pipeline + exploratory data analysis

1. Write backend/data_pipeline/preprocess.py:
   - Load filtered CSVs from backend/data/filtered/
   - Normalize timestamps to a single timezone/format
   - Join logon/file/device events per user per day into unified activity 
     records
   - Explicitly handle missing data: document and log the strategy used 
     (e.g., drop vs impute vs flag), never silently drop rows without a 
     printed/logged count
   - Encode categorical features (activity type, app context, etc.) 
     consistently — save the encoding scheme to a config file so 
     PRISM/AIRS can reuse it later
   - Output a clean DataFrame, saved as parquet in backend/data/filtered/processed/

2. Keep this CLI-runnable and config-driven like Week 2's script (`python -m backend.data_pipeline.preprocess`).

3. Build docs/eda.ipynb:
   - Class balance (malicious vs benign activity counts)
   - Activity volume per user
   - Time distribution (business hours vs off-hours)
   - Sanity check: confirm no malicious scenario got truncated by the date 
     window chosen in Week 2
   - Save 3-4 key plots as PNGs into docs/ for later use in the README/report

4. Write backend/tests/test_preprocess.py with synthetic mock data.

5. Update backend/data_pipeline/README.md with the preprocessing step documented.

DELIVERABLE CHECK: A single parquet file that PRISM (Week 4) and AIRS 
(Week 5+) can both load directly without any further ad-hoc cleaning.

Before ending this week: write docs/weekly_logs/weekN.md (replace N with this week's number) following the WEEKLY LOG REQUIREMENT format from the Global Context.
```

---

## WEEK 4 — PRISM Rule-Based Scoring Engine

```
WEEK 4 TASK: Implement PRISM (Privilege-based Risk & Insider Scoring Mechanism)

Reference formula from the paper:
R = (Wp·Sp) + (WA·SA) + (WC·SC) + (WIP·SIP) + (WB·SB) + (WD·SD) + (WCA·SCA)

1. In backend/prism/scorer.py, implement each sub-score as an independently 
   testable, pure function (no side effects, no shared state):
   - user_privilege_score(user_role)
   - activity_type_score(activity_type)
   - application_context_score(app_name)
   - ip_score(ip_address, known_ips_for_user)
   - business_hours_score(timestamp)
   - device_compliance_score(device_id, compliant_device_list)
   - cumulative_activity_score(user_activity_window)

2. In backend/prism/weights.yaml, define all weights as configurable values, not 
   hardcoded in scorer.py.

3. In backend/prism/buckets.py, implement Min-Max normalization to 0-1 scale and 
   risk bucketing (Low/Moderate/High) with configurable thresholds.

4. Write a batch-scoring function that runs PRISM over the full 
   preprocessed dataset from Week 3, producing labeled risk scores per 
   activity — this becomes the training signal for AIRS.

5. Write backend/tests/test_prism.py: unit test each sub-score function, plus a 
   regression test using the paper's worked example (low-privilege 
   employee, unknown IP, SharePoint, 5 files moved, off-hours, 
   non-compliant device → expect ~0.385 normalized score).

6. Produce docs/phase_reports/week4_prism_results.md: score distribution 
   histogram, risk bucket breakdown, and — critically — what % of the 30 
   known-malicious users' activities scored High risk. This is your first 
   real correctness check.

DELIVERABLE CHECK: PRISM must assign meaningfully higher scores to known 
malicious users than to random benign users. If it doesn't, we tune 
backend/prism/weights.yaml before moving to Week 5 — flag this clearly if it happens.

Before ending this week: write docs/weekly_logs/weekN.md (replace N with this week's number) following the WEEKLY LOG REQUIREMENT format from the Global Context.
```

---

## WEEK 5 — AIRS Autoencoder: Architecture + Training Setup

```
WEEK 5 TASK: Build and start training the AIRS autoencoder

1. In backend/airs/config.yaml, define all hyperparameters (layer sizes, learning 
   rate, batch size, epochs, alpha for feedback blending, retrain 
   threshold N) — nothing hardcoded in model.py or train.py.

2. In backend/airs/model.py, build a PyTorch autoencoder class:
   - Input: numeric feature vector per activity (derived from the 
     preprocessed + PRISM-labeled data)
   - Architecture: symmetric encoder/decoder, justify layer sizes in a 
     comment based on feature vector dimensionality
   - Keep the class clean: __init__ builds layers, forward() only does the 
     forward pass, no training logic inside the model class itself

3. In backend/airs/train.py:
   - Train ONLY on benign user activity
   - Train/val split on benign data; hold out all 30 malicious users' data 
     completely as a separate test set — never touch it during training
   - Loss: MSE reconstruction loss
   - Log training/validation loss per epoch, save checkpoints to a 
     gitignored backend/checkpoints/ folder
   - CLI-runnable: `python -m backend.airs.train --config backend/airs/config.yaml`

4. Provide docs/train_colab.ipynb as a free-tier GPU fallback — same 
   training logic, adapted for Colab, in case local hardware is 
   insufficient. Ask me for my local RAM/GPU specs before finalizing model 
   size so training is actually feasible either locally or on Colab's free 
   tier.

5. Write backend/tests/test_airs.py: test model forward pass shapes, test that 
   training loss decreases over a few epochs on a tiny synthetic batch 
   (fast test, not full training).

DELIVERABLE CHECK: A trained checkpoint (even if not fully tuned yet) that 
loads and runs inference on a sample activity without errors.

Before ending this week: write docs/weekly_logs/weekN.md (replace N with this week's number) following the WEEKLY LOG REQUIREMENT format from the Global Context.
```

---

## WEEK 6 — AIRS Scoring, Feedback Loop, Evaluation

```
WEEK 6 TASK: Finish AIRS — scoring, feedback blending, retraining, evaluation

1. In backend/airs/inference.py:
   - Implement SAI = normalize(reconstruction_error), scaled 0-1
   - Function should take a single activity record or a batch, return 
     scores

2. In backend/airs/feedback.py:
   - Implement Sfinal = SAI + alpha*(Suser - SAI), alpha from config
   - Implement a function to accumulate feedback records (store 
     activity_id, SAI, Suser, Sfinal, timestamp)
   - Implement incremental retraining: fine-tune the existing checkpoint 
     using accumulated feedback once N=50 (configurable) instances are 
     collected — do NOT retrain from scratch

3. Evaluate on the held-out malicious set from Week 5:
   - Report false positive rate, true positive rate, false negative rate
   - Compare against PRISM's Week 4 numbers
   - Be strictly honest: report the actual numbers from our smaller 
     dataset, do not adjust results to match the paper's reported 59%/30% 
     improvements. If results are worse, explain likely reasons (dataset 
     size, feature richness, etc.) in the report rather than hiding it.

4. Write docs/phase_reports/week6_airs_results.md with the above, plus a 
   comparison table: PRISM vs AIRS on our dataset.

5. Extend backend/tests/test_airs.py to cover inference.py and feedback.py logic.

DELIVERABLE CHECK: A working score(activity) -> SAI function, a working 
feedback blending function, and an honest evaluation report comparing AIRS 
to PRISM.

Before ending this week: write docs/weekly_logs/weekN.md (replace N with this week's number) following the WEEKLY LOG REQUIREMENT format from the Global Context.
```

---

## WEEK 7 — SHAP Explainability Layer

```
WEEK 7 TASK: Explainability module (backend/explainability/)

This is the project's core differentiator over the original paper — take 
the time to make it solid.

1. In backend/explainability/shap_explainer.py:
   - Wrap SHAP (KernelExplainer or DeepExplainer — pick based on 
     compatibility with the PyTorch autoencoder, document why in a 
     comment) around the AIRS reconstruction error output
   - Function: explain_activity(activity_record) -> ranked list of feature 
     contributions with human-readable feature names (not raw column 
     indices)

2. In backend/explainability/visualize.py:
   - Reusable functions for SHAP summary plots (global feature importance 
     across the dataset) and force plots (per-instance)
   - These should be callable functions returning matplotlib/plotly 
     figures, not one-off notebook cells, so the dashboard (Week 11) and 
     reports can both use them

3. Write backend/tests/test_explainability.py: sanity-check that SHAP contributions 
   are consistent in direction/magnitude with the model's actual output 
   (approximate check, SHAP isn't exact — document the tolerance used).

4. Update backend/explainability/README.md, explicitly framing this module as 
   addressing the "explainable AI" gap the original paper leaves as future 
   work.

DELIVERABLE CHECK: For any activity, explain_activity() reliably returns a 
clear "why" (e.g., "off-hours: 40%, untrusted IP: 25%, unusual file 
volume: 35%") — test this against several of the known malicious users' 
flagged activities and confirm the explanations make intuitive sense.

Before ending this week: write docs/weekly_logs/weekN.md (replace N with this week's number) following the WEEKLY LOG REQUIREMENT format from the Global Context.
```

---

## WEEK 8 — Buffer Week / Model Refinement

```
WEEK 8 TASK: Buffer — use based on where Weeks 5-7 actually landed

By this point, pick whichever applies:

A) If AIRS performance is weak (FPR/TPR not meaningfully better than 
   PRISM): revisit feature engineering (are we using the right signals?), 
   try adjusting the autoencoder architecture or training longer, re-check 
   the benign/malicious split for leakage.

B) If SHAP explanations are inconsistent or slow: consider caching SHAP 
   values for the dataset rather than computing on the fly, or switching 
   explainer type.

C) If both are in good shape: get ahead — start Week 9's Groq setup 
   early, or add 1-2 additional PRISM policy rules to strengthen the 
   comparison baseline.

Whichever applies, do NOT introduce new scope — this week is for hardening 
what already exists, not adding features. Write up 
docs/phase_reports/week8_refinement_notes.md documenting what was 
fixed/improved and why.

DELIVERABLE CHECK: PRISM, AIRS, and SHAP modules are all stable, tested, 
and documented before moving into the LLM/API phase.

Before ending this week: write docs/weekly_logs/weekN.md (replace N with this week's number) following the WEEKLY LOG REQUIREMENT format from the Global Context.
```

---

## WEEK 9 — LLM Integration (Groq API)

```
WEEK 9 TASK: LLM recommendation service (backend/llm_service/)

1. Create a free Groq account, generate an API key, store it in .env as 
   GROQ_API_KEY (never commit this — confirm .gitignore covers .env). 
   Install the groq Python SDK.

2. Test 2-3 candidate open-weight models available on Groq (e.g. 
   llama-3.3-70b-versatile, deepseek-r1-distill-llama-70b, or a smaller/
   faster option like llama-3.1-8b-instant) on a handful of sample risk 
   events. Compare: response quality/coherence, JSON-following reliability, 
   and speed. Pick one as the default and document why in 
   backend/llm_service/README.md — don't just pick the biggest model; factor in 
   Groq's free-tier rate limits (requests/tokens per minute) since a 
   heavier model may throttle faster under repeated testing.

3. Build backend/llm_service/providers/ as an interface so the LLM backend is 
   swappable:
   - backend/llm_service/providers/base.py: an abstract LLMProvider interface (e.g. a 
     `generate_recommendation(prompt: str) -> dict` method)
   - backend/llm_service/providers/groq_provider.py: Groq implementation (the default/active 
     provider)
   - backend/llm_service/providers/ollama_provider.py: stub implementation for local Ollama, 
     matching the same interface, left unimplemented or minimally 
     implemented — this proves the architecture is provider-agnostic even 
     though Groq is what we actually use, and gives contributors an 
     obvious extension point
   - A config value (LLM_PROVIDER=groq in .env) selects which provider is 
     instantiated — no hardcoded provider choice in application logic

4. In backend/llm_service/prompts.py: define prompt templates as separate, 
   versioned constants/functions — never inline prompt strings inside 
   logic code. Template takes: risk score (PRISM + AIRS), SHAP top-3 
   feature contributions, user role, recent activity summary. Ask the 
   model to return structured JSON: {summary, risk_drivers, 
   recommended_action}. Use Groq's JSON mode / structured output support 
   if available for the chosen model, rather than relying purely on prompt 
   instructions.

5. In backend/llm_service/safety.py: sanitize any user-controlled/log-derived data 
   (e.g. filenames, IPs) before inserting into prompts, to prevent prompt 
   injection from log fields — this matters more now since Groq is an 
   external hosted API, not a fully local model.

6. In backend/llm_service/recommend.py: function that calls the active provider 
   (via the interface, not Groq directly), parses the structured JSON 
   response, handles parse failures gracefully (retry once, then fall back 
   to a raw-text response rather than crashing), and handles Groq rate-limit 
   errors gracefully (backoff/retry, clear error surfaced to the API layer 
   rather than a silent failure).

7. Write backend/tests/test_llm_service.py: test prompt template rendering, safety 
   sanitization, and provider selection logic without requiring a live 
   Groq call (mock the provider response for CI-friendliness); a separate 
   manual/integration test script for live testing against the real Groq 
   API.

DELIVERABLE CHECK: Given a sample high-risk activity + its SHAP breakdown, 
recommend() returns a clean, structured recommendation via Groq, and the 
provider interface would let a contributor swap in Ollama without changing 
any calling code.

Before ending this week: write docs/weekly_logs/weekN.md (replace N with this week's number) following the WEEKLY LOG REQUIREMENT format from the Global Context.
```

---

## WEEK 10 — FastAPI Backend

```
WEEK 10 TASK: API layer (backend/api/) tying everything together

1. Set up backend/api/db.py (SQLAlchemy engine/session, SQLite locally) and 
   backend/api/models/ (User, Activity, Score, Feedback, PolicyViolation ORM 
   models).

2. Set up backend/api/schemas/ (Pydantic request/response models — keep separate 
   from ORM models).

3. Build routes, each in its own file under backend/api/routes/:
   - POST /score — run PRISM + AIRS on a submitted activity, return score
   - GET /explain/{activity_id} — return SHAP breakdown
   - GET /recommend/{activity_id} — return LLM recommendation
   - POST /feedback — accept analyst score adjustment, store it, trigger 
     retraining check
   - GET /policy-violations — return recent rule-triggered flags
   - GET /users/{user_id}/history — activity + score history

4. In backend/policy_engine/rules.py and backend/policy_engine/engine.py: implement 4-5 of 
   the paper's policy rules (e.g. mass download, external share, off-hours 
   + high privilege combo, non-compliant device access) as independently 
   testable rule functions, evaluated by the engine against new activity.

5. backend/api/main.py wires routes together, includes basic error handling 
   middleware, structured logging (no bare except blocks), and CORS 
   middleware configured to allow the React dev server origin 
   (localhost:5173 for Vite) plus the deployed frontend origin later.

6. Write backend/tests/test_api.py using FastAPI's TestClient, and 
   backend/tests/test_policy_engine.py for the rule engine.

DELIVERABLE CHECK: POST a sample activity to /score and get back PRISM 
score, AIRS score, SHAP explanation, and LLM recommendation via chained API 
calls — confirm the full pipeline works end-to-end through the API layer.

Before ending this week: write docs/weekly_logs/weekN.md (replace N with this week's number) following the WEEKLY LOG REQUIREMENT format from the Global Context.
```

---

## WEEK 11 — React Dashboard (Part 1: Setup + Core Pages)

```
WEEK 11 TASK: Frontend scaffolding + core pages (frontend/)

1. Scaffold with Vite: `npm create vite@latest frontend -- --template 
   react-ts`. Add Tailwind CSS, Recharts, Axios, React Router, ESLint + 
   Prettier. Set up frontend/.env for the API base URL 
   (VITE_API_BASE_URL), never hardcode the backend URL in components.

2. In frontend/src/types/index.ts: define TypeScript interfaces mirroring 
   the backend's Pydantic schemas exactly (Activity, RiskScore, 
   ShapExplanation, Recommendation, PolicyViolation, FeedbackSubmission) — 
   keep frontend and backend types in sync; note any mismatch to me 
   explicitly rather than guessing field names.

3. In frontend/src/api/: one file per resource (scoring.ts, feedback.ts, 
   policy.ts), each exporting typed functions (e.g. 
   `getRiskScore(activityId: string): Promise<RiskScore>`) built on a 
   shared axios instance in client.ts. No component should call axios/fetch 
   directly — always go through this layer.

4. Set up React Router in App.tsx with routes for: Overview, User 
   Drilldown, Policy Feed. Keep App.tsx thin — layout/navigation only.

5. Build the Overview page (frontend/src/pages/Overview.tsx):
   - Risk score distribution chart (Recharts)
   - Top 10 highest-risk users table
   - Alert counts by category
   - Use a custom hook (frontend/src/hooks/useOverviewData.ts) for data fetching, keep 
     the component itself focused on rendering

6. Build small reusable components as you go: RiskBadge.tsx (color-coded 
   risk level), a generic DataTable or reuse a simple table component.

7. Write a few component tests in frontend/tests with Vitest + React Testing Library for 
   RiskBadge and the Overview page's loading/error states.

DELIVERABLE CHECK: `npm run dev` in frontend directory against a locally running FastAPI backend 
renders a working Overview page with real data, fully typed, no `any` 
types, lint passes clean.

Before ending this week: write docs/weekly_logs/weekN.md (replace N with this week's number) following the WEEKLY LOG REQUIREMENT format from the Global Context.
```

---

## WEEK 11B — React Dashboard (Part 2: Drilldown, Feedback, Policy Feed)

```
If Week 11 core setup finished with time to spare, continue directly into 
this in the same week. Otherwise treat this as an extension into the start 
of Week 12's buffer — flag which happened.

WEEK 11B TASK: Remaining dashboard pages + interactivity

1. Build UserDrilldown.tsx (frontend/src/pages/UserDrilldown.tsx):
   - User selector (dropdown/search)
   - ActivityTimeline.tsx component showing the user's activity + score 
     history over time (Recharts line/scatter)
   - ShapExplanationPanel.tsx: renders the SHAP feature contribution 
     breakdown for a selected activity (bar chart + plain-language summary)
   - Displays the LLM recommendation for flagged activities

2. Build FeedbackPanel.tsx (likely embedded within UserDrilldown rather 
   than a separate page):
   - ScoreSlider.tsx component: lets the analyst adjust a risk score, 
     submits to POST /feedback via api/feedback.ts
   - Show clear success/error state after submission

3. Build PolicyFeed.tsx (frontend/src/pages/PolicyFeed.tsx):
   - Table of recent policy violations with rule name, trigger condition, 
     simulated action taken, timestamp
   - Basic filtering (by severity/category)

4. Add loading states, error boundaries, and empty states across all pages 
   — do not let the UI silently fail if the API is unreachable or returns 
   no data.

5. Write a manual QA checklist (docs/phase_reports/week11_dashboard_qa.md) 
   covering each page/interaction, since UI is harder to fully unit test — 
   I'll walk through this checklist myself.

DELIVERABLE CHECK: A fully clickable React app covering the entire 
pipeline — overview, drilldown with SHAP + LLM recommendation, feedback 
submission, and policy feed — all typed, linted, and running against the 
local FastAPI backend.

Before ending this week: write docs/weekly_logs/weekN.md (replace N with this week's number) following the WEEKLY LOG REQUIREMENT format from the Global Context.
```

---

## WEEK 12 — Dockerization + Free-Tier Deployment

```
WEEK 12 TASK: Containerize and deploy on free tiers

1. docker/Dockerfile.api and docker/Dockerfile.frontend: separate, minimal 
   images for the API and the React app (multi-stage build for the 
   frontend: `npm run build` then serve the static output via nginx or a 
   lightweight static server).

2. docker/docker-compose.yml: spin up API + Postgres (or SQLite volume) + 
   frontend together, so `docker-compose up` gives a fully working local 
   system, with the frontend's VITE_API_BASE_URL pointed at the 
   containerized API. Note: Ollama is NOT included in this compose file — 
   since Week 9 made Groq the active provider, the deployed and 
   docker-compose setups both use Groq (via GROQ_API_KEY in .env), so 
   there's no need to containerize a local LLM. If a contributor wants to 
   run fully offline with Ollama instead, document that as a manual 
   optional step in the README (install Ollama separately, set 
   LLM_PROVIDER=ollama in .env).

3. Deploy the demo using free tiers:
   - Backend: Render free tier or a Hugging Face Space (Docker SDK) — this 
     now works cleanly since the API only calls out to Groq's hosted API 
     rather than needing to run a local model, so there's no GPU/RAM 
     constraint on the hosting side
   - Database: Neon or Supabase free Postgres tier
   - Frontend: Vercel or Netlify free tier (both have excellent free-tier 
     support for Vite/React static builds, faster and simpler than 
     containerizing the frontend for deployment even though Docker is used 
     locally)
   - Set GROQ_API_KEY as a secret/environment variable on whichever backend 
     host you choose — never in code, never in the Docker image itself
   - Make sure CORS on the deployed API allows the deployed frontend's 
     origin (Vercel/Netlify URL)
   - Watch Groq's free-tier rate limits under real demo traffic — if the 
     deployed demo could get meaningful public traffic (e.g. shared on 
     LinkedIn/resume), consider adding a short response cache (e.g. cache 
     recommend() results per activity_id for repeat views) so repeated 
     dashboard visits don't burn through rate limits unnecessarily. 
     Implement this cache regardless — it's good practice, not just a 
     rate-limit workaround.

4. Write backend/tests/test_e2e.py: a small end-to-end test running the full 
   pipeline (ingest → score → explain → recommend) on a tiny held-out 
   sample, runnable in CI, with the Groq call mocked so CI doesn't depend 
   on a live API key.

5. Set up a basic GitHub Actions workflow (.github/workflows/ci.yml) 
   running lint + tests on every push.

DELIVERABLE CHECK: A live, shareable demo link with fully working, live LLM 
recommendations via Groq (no caching workaround needed), plus a fully 
working local docker-compose setup that a contributor can run with one 
command after adding their own free Groq API key to .env.

Before ending this week: write docs/weekly_logs/weekN.md (replace N with this week's number) following the WEEKLY LOG REQUIREMENT format from the Global Context.
```

---

## WEEK 13 — Documentation, Polish, Open-Sourcing

```
WEEK 13 TASK: Prepare for public release and resume presentation

1. Finalize README.md:
   - Problem statement, citing the original paper, explicitly stating what 
     gaps this project addresses (explainability, open-source 
     reproducibility, on-prem LLM reasoning detail)
   - Real architecture diagram image (generate from the structure/workflow 
     already defined, not ASCII)
   - Setup instructions (local + Docker, plus separate frontend/backend 
     dev setup for contributors who only want to work on one side)
   - Screenshots/GIF of the React dashboard
   - Results table: PRISM vs AIRS performance on our dataset, with the 
     paper's numbers shown only as a reference point, not a claim of 
     matching them
   - Honest "Limitations" section (dataset size, synthetic data caveats, 
     LLM hosting constraints)

2. Finalize CONTRIBUTING.md with setup steps for new contributors, coding 
   standards (reference the code quality rules), and PR process.

3. Create 5-8 "good first issue" GitHub issues (e.g., "add a new PRISM risk 
   factor", "improve SHAP visualization", "add a new policy rule", "write 
   additional unit tests").

4. Finalize LICENSE (MIT), confirm every module has an up-to-date README.

5. Write docs/project_report.md suitable for adapting into your college 
   project report: introduction, related work (cite the base paper), 
   methodology, results, conclusion, future work.

6. Write a 1-2 paragraph resume/LinkedIn summary highlighting: the specific 
   gap identified in existing research, the technical stack, the 
   measurable outcome (your actual FPR/TPR numbers), and the open-source 
   contributor angle.

7. Final full read-through: confirm every module is documented, tested, 
   and free of dead code/TODOs before tagging the release.

8. Push to GitHub, tag v1.0.0 release.

DELIVERABLE CHECK: A public repo that a stranger could clone, understand, 
and run within 15 minutes using only the README.

Before ending this week: write docs/weekly_logs/weekN.md (replace N with this week's number) following the WEEKLY LOG REQUIREMENT format from the Global Context.
```

---

## Dataset Sizing Reference (carry through Week 2)

| Dimension | Target |
|---|---|
| Malicious users | All 30 available in CERT r4.2 (don't subsample) |
| Benign users | 250–350 (random sample, seed=42) |
| Time window | 6–9 months, sized to fully cover all 30 malicious scenarios |
| Total rows after filtering | ~3–6 million |
| Disk size after filtering | ~2–4 GB |
| Files needed | logon.csv, file.csv, device.csv, users.csv, answers/insiders file |

If your local machine still struggles at this size, drop to 150–200 benign users before dropping below that — do not go under 100 benign users, as the autoencoder needs behavioral variety to avoid learning an artificially narrow "normal" profile.
