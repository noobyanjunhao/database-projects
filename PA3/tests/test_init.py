# import os

# import pytest
# from flask import Flask
# from flask.testing import FlaskCliRunner

# from flaskr import create_app
# from flaskr.db import init_db


# def test_create_app_defaults(app: Flask) -> None:
#     assert app.config["TESTING"]
#     assert app.config["SECRET_KEY"] == "test"
#     assert os.path.exists(app.config["DATABASE"])


# def test_init_db_command(runner: FlaskCliRunner) -> None:
#     result = runner.invoke(args=["init-db"])
#     assert result.exit_code == 0
#     assert "Initialized the database." in result.output


# def test_create_app_with_test_config() -> None:
#     """Test that create_app properly applies a given test config."""
#     test_config = {
#         "TESTING": True,
#         "SECRET_KEY": "mysecret",
#         "DATABASE": "/tmp/mydb.sqlite",
#     }
#     app = create_app(test_config)
#     assert app.config["TESTING"] is True
#     assert app.config["SECRET_KEY"] == "mysecret"
#     assert app.config["DATABASE"] == "/tmp/mydb.sqlite"
"""Tests for app factory and init-db CLI command."""

import os
from flask import Flask
from flask.testing import FlaskCliRunner

from flaskr import create_app  # pylint: disable=import-error


def test_create_app_defaults(app: Flask) -> None:
    """Test that the default app config is correctly set."""
    assert app.config["TESTING"]
    assert app.config["SECRET_KEY"] == "test"
    assert os.path.exists(app.config["DATABASE"])


def test_init_db_command(runner: FlaskCliRunner) -> None:
    """Test that the init-db CLI command works."""
    result = runner.invoke(args=["init-db"])
    assert result.exit_code == 0
    assert "Initialized the database." in result.output


def test_create_app_with_test_config() -> None:
    """Test that create_app properly applies a given test config."""
    test_config = {
        "TESTING": True,
        "SECRET_KEY": "mysecret",
        "DATABASE": "/tmp/mydb.sqlite",
    }
    app = create_app(test_config)
    assert app.config["TESTING"] is True
    assert app.config["SECRET_KEY"] == "mysecret"
    assert app.config["DATABASE"] == "/tmp/mydb.sqlite"
