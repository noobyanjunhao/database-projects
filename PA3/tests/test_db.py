import sqlite3
import pytest
from flaskr.db import get_db, close_db

def test_get_db_returns_same_connection(app):
    with app.app_context():
        c1 = get_db()
        c2 = get_db()
        assert c1 is c2
        assert isinstance(c1, sqlite3.Connection)
        assert c1.row_factory == sqlite3.Row

def test_close_db_removes_and_closes(app):
    with app.app_context():
        conn = get_db()
        close_db()
        with pytest.raises(sqlite3.ProgrammingError):
            conn.execute("SELECT 1")
