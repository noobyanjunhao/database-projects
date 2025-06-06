"""Unit tests for database-related functionality."""

import io
import sqlite3
from unittest.mock import patch

import pytest
from flask import Flask

from flaskr.db import close_db, get_db, init_db  # pylint: disable=import-error


def test_get_db_returns_same_connection(app: Flask) -> None:
    """Test that get_db returns the same connection object within app context."""
    with app.app_context():
        c1 = get_db()
        c2 = get_db()
        assert c1 is c2
        assert isinstance(c1, sqlite3.Connection)
        assert c1.row_factory == sqlite3.Row


def test_close_db_removes_and_closes(app: Flask) -> None:
    """Test that close_db correctly closes and removes the connection."""
    with app.app_context():
        conn = get_db()
        close_db()
        with pytest.raises(sqlite3.ProgrammingError):
            conn.execute("SELECT 1")


def test_init_db_with_string_content(app: Flask) -> None:
    """Test init_db when schema.sql returns string content."""
    with app.app_context():
        string_content = "CREATE TABLE test_string (id INTEGER PRIMARY KEY);"

        with patch.object(app, "open_resource") as mock_open:
            mock_open.side_effect = [
                io.StringIO(string_content),
                io.StringIO("-- Empty seed"),
            ]


            init_db()

            db = get_db()
            result = db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='test_string'"
            ).fetchone()
            assert result is not None
            assert result["name"] == "test_string"
