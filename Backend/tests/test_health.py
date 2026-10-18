from unittest.mock import patch
from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient):
    """Verify GET /health returns 200 and project status info."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["project"] == "SachCheck"


def test_health_db_endpoint_success(client: TestClient):
    """Verify GET /health/db returns 200 when database connectivity check passes."""
    with patch("app.main.check_db_connection", return_value=(True, "Database connectivity check passed.")):
        response = client.get("/health/db")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["project"] == "SachCheck"
        assert "Database connectivity check passed" in data["database"]


def test_health_db_endpoint_failure(client: TestClient):
    """Verify GET /health/db returns 503 when database connectivity check fails."""
    with patch("app.main.check_db_connection", return_value=(False, "Connection refused")):
        response = client.get("/health/db")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "error"
        assert data["project"] == "SachCheck"
        assert "Connection refused" in data["database"]
