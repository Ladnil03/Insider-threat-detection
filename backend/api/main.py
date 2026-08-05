"""FastAPI Application Entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import explain, feedback, policy, recommend, score

app = FastAPI(
    title="OpenIRM API",
    description="AI-Driven Insider Risk Management System REST Service",
    version="0.1.0",
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include route routers
app.include_router(score.router, prefix="/api/v1", tags=["scoring"])
app.include_router(explain.router, prefix="/api/v1", tags=["explainability"])
app.include_router(recommend.router, prefix="/api/v1", tags=["llm"])
app.include_router(feedback.router, prefix="/api/v1", tags=["feedback"])
app.include_router(policy.router, prefix="/api/v1", tags=["policy"])


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        Dictionary confirming API service health status.
    """
    return {"status": "ok", "system": "OpenIRM API"}
