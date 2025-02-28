import sqlite3
import pytest
from flask import Flask
from flaskr.db import get_db
from typing import Any, Dict, Generator

def test_get_close_db(app: Flask) -> None:
    """Test database connection is closed after context."""
    with app.app_context():
        db = get_db()
        assert db is get_db()
        
    # Explicitly close the database connection
    db.close()

    # Try to execute a query after the context is closed
    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')
    
    assert 'closed' in str(e.value)

def test_database_content(app: Flask) -> None:
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

