# LLM Service

Orchestrates risk score + SHAP explanation + user context into a plain-English analyst recommendation via a configurable LLM provider.

**Providers:**
- `groq_provider` — Groq API (free tier, default)
- `ollama_provider` — local Ollama (on-prem fallback)

**Interface:** `BaseProvider` in `providers/base.py` — add new providers without touching the orchestration logic.
