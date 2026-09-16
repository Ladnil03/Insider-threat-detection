"""Integration Tests for OpenIRM FastAPI Service Layer Endpoints."""

import pytest
from fastapi.testclient import TestClient

from api.db import init_db
from api.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Initializes clean database schema for each test session."""
    init_db()


def test_health_endpoint() -> None:
    """Tests /health status endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["system"] == "OpenIRM API Service"


def test_score_activity_endpoint_end_to_end() -> None:
    """Tests /api/v1/score endpoint with full activity telemetry."""
    payload = {
        "user_id": "ACM2278",
        "date_day": "2026-08-15",
        "user_role": "Senior Systems Engineer",
        "metrics": {
            "file_copy_usb": 85,
            "logon_after_hours": 6,
            "email_external_count": 18,
            "email_large_attachment_count": 4,
            "file_copy_usb_baseline_dev": 3.8,
            "logon_after_hours_baseline_dev": 3.2,
        },
    }

    response = client.post("/api/v1/score", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert data["user_id"] == "ACM2278"
    assert "activity_id" in data
    assert data["activity_id"] > 0
    assert 0.0 <= data["prism_score"] <= 1.0
    assert 0.0 <= data["airs_score"] <= 1.0
    assert 0.0 <= data["ensemble_score"] <= 1.0
    assert data["risk_level"] in ["LOW", "MODERATE", "HIGH", "CRITICAL"]

    # Verify triggered policies
    policies = data.get("triggered_policies", [])
    assert len(policies) > 0
    rule_ids = {p["rule_id"] for p in policies}
    assert "RULE-USB-EXFIL" in rule_ids


def test_explain_activity_endpoint() -> None:
    """Tests GET /api/v1/explain/{activity_id} returns structured SHAP explanation."""
    # 1. First score an activity to generate activity_id
    score_res = client.post(
        "/api/v1/score",
        json={
            "user_id": "EXPLAIN_TEST_USER",
            "metrics": {"file_copy_usb": 75, "logon_after_hours": 5},
        },
    )
    activity_id = score_res.json()["activity_id"]

    # 2. Query explain route
    response = client.get(f"/api/v1/explain/{activity_id}?top_k=3")
    assert response.status_code == 200
    data = response.json()

    assert data["activity_id"] == activity_id
    assert data["user_id"] == "EXPLAIN_TEST_USER"
    assert "reconstruction_error" in data
    assert "sai_score" in data
    assert "human_readable_summary" in data
    assert len(data["features"]) > 0


def test_recommend_activity_endpoint() -> None:
    """Tests GET /api/v1/recommend/{activity_id} returns LLM analyst recommendation."""
    # 1. Score an activity
    score_res = client.post(
        "/api/v1/score",
        json={
            "user_id": "REC_TEST_USER",
            "metrics": {"file_copy_usb": 120, "web_job_search_count": 15},
        },
    )
    activity_id = score_res.json()["activity_id"]

    # 2. Query recommend route
    response = client.get(f"/api/v1/recommend/{activity_id}")
    assert response.status_code == 200
    data = response.json()

    assert data["activity_id"] == activity_id
    assert data["user_id"] == "REC_TEST_USER"
    assert "summary" in data
    assert "recommended_action" in data
    assert "urgency" in data


def test_feedback_submission_and_blending() -> None:
    """Tests POST /api/v1/feedback accepts risk score adjustment and blends feedback."""
    # 1. Score an activity
    score_res = client.post(
        "/api/v1/score",
        json={
            "user_id": "FB_TEST_USER",
            "metrics": {"logon_count": 5},
        },
    )
    activity_id = score_res.json()["activity_id"]
    orig_score = score_res.json()["ensemble_score"]

    # 2. Submit analyst adjustment
    feedback_payload = {
        "activity_id": activity_id,
        "user_id": "FB_TEST_USER",
        "adjusted_score": 0.85,
        "notes": "Verified unauthorized USB drive connection.",
    }
    response = client.post("/api/v1/feedback", json=feedback_payload)
    assert response.status_code == 201
    data = response.json()

    assert data["activity_id"] == activity_id
    assert data["adjusted_score"] == 0.85
    # Blended score = 0.3 * orig + 0.7 * 0.85
    expected_blended = round(0.3 * orig_score + 0.7 * 0.85, 4)
    assert abs(data["blended_score"] - expected_blended) < 0.05
    assert data["notes"] == "Verified unauthorized USB drive connection."


def test_policy_violations_endpoint() -> None:
    """Tests GET /api/v1/policy-violations returns audit logs."""
    # Trigger a violation
    client.post(
        "/api/v1/score",
        json={
            "user_id": "VIOLATION_USER",
            "metrics": {"file_copy_usb": 90},
        },
    )

    response = client.get("/api/v1/policy-violations?limit=10")
    assert response.status_code == 200
    violations = response.json()
    assert isinstance(violations, list)
    assert len(violations) >= 1
    assert any(v["rule_id"] == "RULE-USB-EXFIL" for v in violations)


def test_users_directory_and_history_endpoints() -> None:
    """Tests GET /api/v1/users and GET /api/v1/users/{user_id}/history."""
    user_id = "TIMELINE_USER"
    client.post(
        "/api/v1/score",
        json={
            "user_id": user_id,
            "date_day": "2026-08-01",
            "metrics": {"logon_count": 3},
        },
    )
    client.post(
        "/api/v1/score",
        json={
            "user_id": user_id,
            "date_day": "2026-08-02",
            "metrics": {"file_copy_usb": 60},
        },
    )

    # 1. Directory
    users_resp = client.get("/api/v1/users")
    assert users_resp.status_code == 200
    user_list = users_resp.json()
    assert any(u["user_id"] == user_id for u in user_list)

    # 2. Timeline history
    history_resp = client.get(f"/api/v1/users/{user_id}/history")
    assert history_resp.status_code == 200
    history_data = history_resp.json()
    assert history_data["user_id"] == user_id
    assert len(history_data["history"]) >= 2
    assert len(history_data["policy_violations"]) >= 1


def test_not_found_error_handling() -> None:
    """Tests 404 errors for non-existent activities and users."""
    exp_resp = client.get("/api/v1/explain/999999")
    assert exp_resp.status_code == 404

    rec_resp = client.get("/api/v1/recommend/999999")
    assert rec_resp.status_code == 404

    user_resp = client.get("/api/v1/users/NON_EXISTENT_USER/history")
    assert user_resp.status_code == 404


def test_chained_pipeline_e2e_flow() -> None:
    """Deliverable Check: Full pipeline chained flow

    /score -> /explain/{id} -> /recommend/{id} -> /feedback.
    """
    # 1. Submit activity to score
    score_resp = client.post(
        "/api/v1/score",
        json={
            "user_id": "CHAIN_USER_001",
            "user_role": "Database Administrator",
            "metrics": {
                "file_copy_usb": 110,
                "logon_after_hours": 7,
                "file_sensitive_access": 15,
                "email_large_attachment_count": 5,
            },
        },
    )
    assert score_resp.status_code == 201
    score_data = score_resp.json()
    activity_id = score_data["activity_id"]

    # 2. Get SHAP explanation
    explain_resp = client.get(f"/api/v1/explain/{activity_id}")
    assert explain_resp.status_code == 200
    explain_data = explain_resp.json()
    assert len(explain_data["top_risk_drivers"]) > 0

    # 3. Get LLM recommendation
    rec_resp = client.get(f"/api/v1/recommend/{activity_id}")
    assert rec_resp.status_code == 200
    rec_data = rec_resp.json()
    assert rec_data["recommended_action"] != ""

    # 4. Submit analyst feedback
    fb_resp = client.post(
        "/api/v1/feedback",
        json={
            "activity_id": activity_id,
            "user_id": "CHAIN_USER_001",
            "adjusted_score": 0.95,
            "notes": "Confirmed malicious insider exfiltration.",
        },
    )
    assert fb_resp.status_code == 201
    fb_data = fb_resp.json()
    assert fb_data["blended_score"] > 0.80
