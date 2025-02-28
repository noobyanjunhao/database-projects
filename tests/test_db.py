import sqlite3
import pytest
from flask import Flask
from flaskr.db import get_db, init_app, initialize_northwind, close_db

# Patch function to wrap close_db so it can accept an argument.
def patched_close_db(e=None):
    # Call the original close_db without passing any argument.
    close_db()

def test_get_close_db(app: Flask) -> None:
    """Test that after explicitly calling close_db, the database connection is closed."""
    with app.app_context():
        db = get_db()
        # Subsequent calls return the same connection.
        assert db is get_db()
        # Explicitly close the connection.
        close_db()
        with pytest.raises(sqlite3.ProgrammingError) as e:
            db.execute("SELECT 1")
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

def test_init_app(app: Flask) -> None:
    """Test that init_app registers the close_db function correctly via teardown."""
    # Patch the teardown function so it accepts the extra argument.
    from flaskr import db as db_module
    db_module.close_db = patched_close_db
    init_app(app)
    with app.app_context():
        conn = get_db()
    # When the context exits, Flask calls the patched teardown (which calls close_db without arguments).
    with pytest.raises(sqlite3.ProgrammingError) as e:
        conn.execute("SELECT 1")
    assert 'closed' in str(e.value)

def test_initialize_northwind(app: Flask) -> None:
    """Test that initialize_northwind creates required tables and inserts the default employee."""
    with app.app_context():
        db = get_db()
        # Drop and re-create the Employees table with a compatible schema.
        db.execute("DROP TABLE IF EXISTS Employees")
        db.execute("""
            CREATE TABLE Employees (
                EmployeeID INTEGER PRIMARY KEY,
                LastName TEXT NOT NULL,
                FirstName TEXT NOT NULL
            )
        """)
        db.commit()
        # Call initialize_northwind which should insert the default employee.
        initialize_northwind()
        emp = db.execute("SELECT * FROM Employees WHERE EmployeeID = 999999").fetchone()
        assert emp is not None
        assert emp["LastName"] == "WEB"
        assert emp["FirstName"] == "WEB"
