import os
import tempfile
import pytest
import sys
import tempfile
from flaskr import create_app
from flaskr.db import get_db
from flask import Flask

# 读取 `data.sql` 文件的内容
with open(os.path.join(os.path.dirname(__file__), "data.sql"), "r", encoding="utf8") as f:
    _data_sql = f.read()

@pytest.fixture
def app():
    """Create a Flask test app and use a temporary database."""
    db_fd, db_path = tempfile.mkstemp()  # Create a temporary database file

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,  # Specify the temporary database path
    })

    with app.app_context():
        # Ensure the database is empty before inserting data
        #get_db().executescript('DELETE FROM Customers;')  # Clear existing data
        get_db().executescript(_data_sql)  # Insert test data from `data.sql`

    yield app

    os.close(db_fd)
    os.unlink(db_path)  # Remove the temporary database file

@pytest.fixture
def client(app):
    """创建 Flask 测试客户端"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """创建 Flask CLI 运行器"""
    return app.test_cli_runner()

@pytest.fixture
def auth(client):
    """A fixture to handle authentication for tests."""
    def login(username, password):
        return client.post('/auth/login', data={'username': username, 'password': password})

    return login

