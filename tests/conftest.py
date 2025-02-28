import os
import tempfile
import pytest
import sys
from flaskr import create_app
from flaskr.db import get_db
from flask import Flask
import sqlite3
from typing import Generator, Callable, Any

# 读取 `data.sql` 文件的内容
with open(
    os.path.join(os.path.dirname(__file__), "data.sql"), "r", encoding="utf8"
) as f:
    _data_sql = f.read()


@pytest.fixture
def app() -> Generator[Flask, None, None]:
    """Create a Flask test app and use a temporary database."""
    db_fd, db_path = tempfile.mkstemp()  # Create a temporary database file

    # First create an initial database with tables and test data
    db = sqlite3.connect(db_path)
    try:
        db.executescript(_data_sql)  # Create tables and insert test data
        db.commit()
    except Exception as e:
        print(f"Error initializing test database: {e}")
        raise
    finally:
        db.close()

    # Now create the app with the pre-initialized database
    app = create_app(
        {
            "TESTING": True,
            "DATABASE": db_path,  # Specify the temporary database path
        }
    )

    yield app

    os.close(db_fd)
    os.unlink(db_path)  # Remove the temporary database file


@pytest.fixture
def client(app: Flask) -> Any:
    """创建 Flask 测试客户端"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """创建 Flask CLI 运行器"""
    return app.test_cli_runner()


@pytest.fixture
def auth(client: Any) -> Callable[[str, str], Any]:
    """A fixture to handle authentication for tests."""

    def login(username: str, password: str) -> Any:
        return client.post(
            "/user/login", data={"username": username, "password": password}
        )

    return login
