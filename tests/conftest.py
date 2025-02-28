"""Test configuration for setting up the Flask app, database, and authentication fixtures."""

import os
import tempfile
import sqlite3
from typing import Generator, Callable, Any

import pytest
from flask import Flask

from flaskr import create_app


# 读取 `data.sql` 文件的内容
with open(os.path.join(os.path.dirname(__file__), "data.sql"), "r", encoding="utf8") as f:
    _data_sql = f.read()


@pytest.fixture
def app() -> Generator[Flask, None, None]:
    """Create a Flask test app with a temporary database."""
    db_fd, db_path = tempfile.mkstemp()  # 创建临时数据库文件

    # 初始化数据库
    db = sqlite3.connect(db_path)
    try:
        db.executescript(_data_sql)  # 执行 SQL 脚本，创建表并插入测试数据
        db.commit()
    except Exception as e:
        print(f"Error initializing test database: {e}")
        raise
    finally:
        db.close()

    # 创建 Flask 应用实例，并指定数据库路径
    app_instance = create_app(
        {
            "TESTING": True,
            "DATABASE": db_path,  # 指定临时数据库路径
        }
    )

    yield app_instance

    os.close(db_fd)
    os.unlink(db_path)  # 删除临时数据库文件


@pytest.fixture
def client(app: Flask) -> Any:
    """Create a Flask test client."""
    return app.test_client()


@pytest.fixture
def runner(app: Flask) -> Any:
    """Create a Flask CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def auth(client: Flask) -> Callable[[str, str], Any]:
    """A fixture to handle user authentication for tests."""

    def login(username: str, password: str) -> Any:
        """Login helper function for test authentication."""
        return client.post(
            "/user/login", data={"username": username, "password": password}
        )

    return login
