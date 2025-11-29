from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Welcome to Interview4 App"


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_info():
    response = client.get("/info")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "Interview4"
    assert data["version"] == "1.0.0"