"""Tests für die Endpunkte des Beispielservice."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    """Given der Service läuft, when /health, then status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_items_returns_all_items() -> None:
    """Given drei Items, when /items, then alle drei mit Feldern."""
    response = client.get("/items")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 3
    assert set(body[0]) == {"id", "name", "category"}
