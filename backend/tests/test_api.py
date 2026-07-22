"""Tests for the FastAPI endpoints."""

from fastapi.testclient import TestClient

from backend.api.main import app

client = TestClient(app)


class TestHealth:
    """Health-check endpoint tests."""

    def test_health_returns_ok(self) -> None:
        """Verify the /health endpoint returns ok."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
