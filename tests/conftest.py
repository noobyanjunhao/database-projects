import os
import pytest
import sys
import tempfile
from flaskr import create_app
from flaskr.db import get_db, init_db

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

_data_sql = """
INSERT INTO user (username, password) VALUES
('testuser', 'testpass');
INSERT INTO product (name, price) VALUES
('Test Product', 999);
"""

@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

