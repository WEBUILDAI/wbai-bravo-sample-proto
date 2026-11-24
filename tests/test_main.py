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


def test_items_filtered_by_category() -> None:
    """Given 2x bauteil, 1x werkzeug, when ?category=bauteil, then zwei bauteil-Items."""
    response = client.get("/items", params={"category": "bauteil"})
    assert response.status_code == 200
    body = response.json()
    assert [item["id"] for item in body] == [1, 2]
    assert all(item["category"] == "bauteil" for item in body)


def test_items_unknown_category_returns_empty_list() -> None:
    """Given dieselben Items, when ?category=gibtsnicht, then 200 und leere Liste."""
    response = client.get("/items", params={"category": "gibtsnicht"})
    assert response.status_code == 200
    assert response.json() == []


def test_items_category_is_case_sensitive() -> None:
    """Given Kategorie bauteil, when ?category=Bauteil, then leere Liste."""
    response = client.get("/items", params={"category": "Bauteil"})
    assert response.status_code == 200
    assert response.json() == []


def test_items_empty_category_is_rejected() -> None:
    """Given dieselben Items, when ?category= (leer), then 422."""
    response = client.get("/items?category=")
    assert response.status_code == 422
