"""Tests for the FastAPI application."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_read_root():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the AI Tutor API"}


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_read_items():
    """Test getting all items."""
    response = client.get("/items/")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_read_item():
    """Test getting a specific item."""
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Item 1"


def test_read_item_not_found():
    """Test getting a non-existent item."""
    response = client.get("/items/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"