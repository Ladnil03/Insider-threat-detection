"""FastAPI application entrypoint.

Mounts all route modules and configures middleware (CORS, logging).
Start with: uvicorn backend.api.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="OpenIRM API",
    description=(
        "AI-Driven Insider Risk Management — scoring, explainability, "
        "and LLM recommendations"
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ponytail: open during development; lock down in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict:
    """Liveness probe."""
    return {"status": "ok"}
