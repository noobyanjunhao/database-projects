"""Module tests for factory configuration and hello endpoint."""

from flask import Flask
from flask.testing import FlaskClient
from flaskr import create_app


def test_config(app: Flask) -> None:
    """Test configuration: ensure the application testing mode is set appropriately."""
    assert not create_app().testing
    assert app.testing


def test_hello(client: FlaskClient) -> None:
    """Test that the /hello endpoint returns the expected greeting."""
    response = client.get("/hello")
    assert response.data == b"Hello, World!"
