"""Tests for main page routes."""
from flask.testing import FlaskClient


def test_index_route(client: FlaskClient) -> None:
    """Test that the index page loads successfully."""
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"<html" in resp.data.lower()


def test_dashboard_route(client: FlaskClient) -> None:
    """Test that the dashboard page loads successfully."""
    resp = client.get("/dashboard")
    assert resp.status_code == 200
    assert b"<html" in resp.data.lower()
