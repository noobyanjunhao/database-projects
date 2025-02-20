import sqlite3
import pytest
from flaskr.db import get_db

def test_get_close_db(app):
    """测试数据库连接是否正确打开和关闭"""
    with app.app_context():
        db = get_db()
        assert db is get_db()  # 确保 `get_db()` 在同一请求内返回相同的数据库连接

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute("SELECT 1")  # 请求结束后，数据库连接应该关闭

    assert "closed" in str(e.value)

def test_database_content(app):
    """测试数据库是否正确插入了测试数据"""
    with app.app_context():
        db = get_db()

        # 检查 Customers 表
        customer = db.execute("SELECT * FROM Customers WHERE CustomerID = 'CUST1'").fetchone()
        assert customer is not None
        assert customer["CompanyName"] == "Tech Solutions"

        # 检查 Products 表
        product = db.execute("SELECT * FROM Products WHERE ProductName = 'Wireless Mouse'").fetchone()
        assert product is not None
        assert product["UnitPrice"] == 25.99

