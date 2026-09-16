"""Pydantic Schemas for SHAP Explainability Endpoints."""

from typing import Any, Dict, List

from pydantic import BaseModel, Field


class FeatureAttribution(BaseModel):
    """Local attribution metrics for a specific feature."""

    feature: str
    raw_key: str
    attribution: float
    value: float
    percentage: float
    direction: str


class ExplainResponse(BaseModel):
    """Complete structured SHAP explanation response."""

    activity_id: int
    user_id: str
    base_value: float
    reconstruction_error: float
    sai_score: float
    human_readable_summary: str
    top_risk_drivers: List[Dict[str, Any]] = Field(default_factory=list)
    features: List[FeatureAttribution] = Field(default_factory=list)
