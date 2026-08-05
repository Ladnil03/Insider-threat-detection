"""Integration Tests for FastAPI Endpoints."""

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    """Tests /health status endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_score_endpoint() -> None:
    """Tests /api/v1/score endpoint."""
    response = client.post("/api/v1/score", json={"user_id": "USR-001"})
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "USR-001"
    assert "composite_score" in data
