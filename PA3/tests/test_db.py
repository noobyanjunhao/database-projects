# tests/test_db.py

import os
import sqlite3
import sys
import pytest
from flask import Flask, g

# Make sure we can import your package
sys.path.insert(0, os.getcwd())

import flaskr.db as db_module

@pytest.fixture
def app(tmp_path):
    """Create and configure a new Flask app instance for testing."""
    # Point root_path at the flaskr package so open_resource finds schema.sql
    pkg_dir = os.path.join(os.getcwd(), 'flaskr')
    app = Flask(__name__,
                root_path=pkg_dir,
                instance_path=str(tmp_path),
                instance_relative_config=True)
    os.makedirs(app.instance_path, exist_ok=True)

    # Configure the test database file
    db_file = tmp_path / "test.sqlite"
    app.config['DATABASE'] = str(db_file)

    # Register teardown and CLI commands
    db_module.init_app(app)
    return app

def test_get_db_returns_same_connection(app):
    """get_db() should return the same sqlite3.Connection object per request."""
    with app.app_context():
        conn1 = db_module.get_db()
        conn2 = db_module.get_db()
        assert conn1 is conn2
        assert isinstance(conn1, sqlite3.Connection)
        assert conn1.row_factory == sqlite3.Row

def test_close_db_removes_and_closes(app):
    """close_db() should pop g.db and close the connection."""
    with app.app_context():
        conn = db_module.get_db()
        db_module.close_db()
        assert 'db' not in g
        with pytest.raises(sqlite3.ProgrammingError):
            conn.execute("SELECT 1")

def test_init_db_command_creates_tables(app):
    """The 'init-db' CLI command initializes schema.sql into the database."""
    runner = app.test_cli_runner()
    result = runner.invoke(args=['init-db'])
    assert result.exit_code == 0
    assert 'Initialized the database.' in result.output

    # Verify that at least the Apartment table exists
    conn = sqlite3.connect(app.config['DATABASE'])
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='Apartment';"
    )
    assert cur.fetchone() is not None

def test_init_app_registers_teardown_and_command(app):
    """init_app() wires up close_db as teardown and registers the init-db CLI."""
    # Teardown
    assert db_module.close_db in app.teardown_appcontext_funcs

    # CLI command
    assert 'init-db' in app.cli.commands
