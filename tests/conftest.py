import os
import tempfile
import pytest
import sys
import tempfile
from flaskr import create_app
from flaskr.db import get_db, init_db

<<<<<<< HEAD
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
=======
# 读取 `data.sql` 文件的内容
with open(os.path.join(os.path.dirname(__file__), "data.sql"), "r", encoding="utf8") as f:
    _data_sql = f.read()

@pytest.fixture
def app():
    """创建 Flask 测试应用，并使用临时数据库"""
    db_fd, db_path = tempfile.mkstemp()  # 创建临时数据库文件

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,  # 指定临时数据库路径
    })

    with app.app_context():
        init_db()  # 初始化数据库结构
        get_db().executescript(_data_sql)  # 插入 `data.sql` 的测试数据

    yield app  # 运行测试

    os.close(db_fd)
    os.unlink(db_path)  # 测试结束后删除临时数据库

@pytest.fixture
def client(app):
    """创建 Flask 测试客户端"""
>>>>>>> 9c45895 (test data sql)
    return app.test_client()

@pytest.fixture
def runner(app):
<<<<<<< HEAD
=======
    """创建 Flask CLI 运行器"""
>>>>>>> 9c45895 (test data sql)
    return app.test_cli_runner()

