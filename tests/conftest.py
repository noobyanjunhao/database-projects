# tests/conftest.py
import os
import pytest
from flaskr import create_app
from flaskr.db import get_db

@pytest.fixture
def app():
    # Create the Flask app with a special test config
    app = create_app({
        'TESTING': True,
        'DATABASE': ':memory:',  # Use an in-memory database
    })

    with app.app_context():
        db = get_db()
        
        # Initialize the database schema
        with open('flaskr/schema.sql', 'r') as f:
            db.executescript(f.read())
        
        # Optionally, load data from northwind.db if needed
        # You can use a similar approach to load data if required

    yield app  # yield the app for the test
    # No need to tear down the in-memory database


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands (if you have any)."""
    return app.test_cli_runner()
