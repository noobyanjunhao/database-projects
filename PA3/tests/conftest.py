"""Pytest fixtures for the project."""

import io
import os
import sys
from typing import IO, Any, Generator, cast

sys.path.insert(0, os.getcwd()) # pylint: disable=wrong-import-position
import pytest
from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner

from flaskr import create_app  # pylint: disable=import-error
from flaskr.db import get_db, init_db  # pylint: disable=import-error


@pytest.fixture
def app(tmp_path) -> Generator[Flask, None, None]:
    """Create a new Flask app instance configured for testing."""
    instance = tmp_path / "instance"
    instance.mkdir()
    db_file = tmp_path / "test.sqlite"

    app = create_app()  # pylint: disable=redefined-outer-name
    app.config.update(
        {
            "TESTING": True,
            "DATABASE": str(db_file),
            "SECRET_KEY": "test",
        }
    )
    app.instance_path = str(instance)

    real_open = app.open_resource

    def fake_open(path: str, mode: str = "rb") -> IO[bytes]:
        """Mock open_resource to skip loading seed.sql during tests."""
        if path.endswith("seed.sql"):
            return io.BytesIO(b"")
        return real_open(path, mode)

    setattr(app, "open_resource", cast(Any, fake_open))

    with app.app_context():
        init_db()
        db = get_db()
        data_sql = os.path.join(os.getcwd(), "tests", "data.sql")
        with open(data_sql, "rb") as f:
            db.executescript(f.read().decode("utf8"))

    yield app


@pytest.fixture
def client(app: Flask) -> FlaskClient:  # pylint: disable=redefined-outer-name
    """Return a test client for making HTTP requests to the app."""
    return app.test_client()


@pytest.fixture
def runner(app: Flask) -> FlaskCliRunner:  # pylint: disable=redefined-outer-name
    """Return a test CLI runner for invoking Flask CLI commands."""
    return app.test_cli_runner()
