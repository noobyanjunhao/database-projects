from flask.testing import FlaskClient


def test_index_route(client: FlaskClient) -> None:
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"<html" in resp.data.lower()


def test_dashboard_route(client: FlaskClient) -> None:
    resp = client.get("/dashboard")
    assert resp.status_code == 200
    assert b"<html" in resp.data.lower()
