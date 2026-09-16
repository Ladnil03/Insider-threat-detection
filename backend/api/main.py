"""FastAPI Application Entrypoint for OpenIRM REST Service."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.db import init_db
from api.routes import explain, feedback, policy, recommend, score, users

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("openirm.api")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup and shutdown lifecycle management."""
    logger.info("Initializing OpenIRM Database schema...")
    try:
        init_db()
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
    yield
    logger.info("Shutting down OpenIRM API service.")


app = FastAPI(
    title="OpenIRM API",
    description="AI-Driven Insider Risk Management System REST Service (Koli et al., arXiv:2505.03796 reproduction + SHAP XAI)",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS Configuration for local React Vite dev server and deployed frontend
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    """Global request error handling middleware logging unhandled exceptions."""
    try:
        response = await call_next(request)
        return response
    except Exception as exc:
        logger.error(
            f"Unhandled exception during request {request.method} {request.url.path}: {exc}",
            exc_info=True,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "InternalServerError",
                "message": "An unexpected error occurred while processing the request.",
                "path": request.url.path,
            },
        )


# Register all API Route Routers under /api/v1
app.include_router(score.router, prefix="/api/v1", tags=["scoring"])
app.include_router(explain.router, prefix="/api/v1", tags=["explainability"])
app.include_router(recommend.router, prefix="/api/v1", tags=["recommendations"])
app.include_router(feedback.router, prefix="/api/v1", tags=["feedback"])
app.include_router(policy.router, prefix="/api/v1", tags=["policy"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])


@app.get("/health", tags=["system"], summary="System health check endpoint")
def health_check() -> Dict[str, str]:
    """Returns basic system health status."""
    return {
        "status": "ok",
        "system": "OpenIRM API Service",
        "version": "0.1.0",
    }
