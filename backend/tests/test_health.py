"""Pruebas del endpoint de salud y raiz."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_root_ok():
    response = client.get("/")
    assert response.status_code == 200
    assert "app" in response.json()
