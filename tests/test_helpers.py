"""Helper functions for test modules.

This module contains helper functions to verify that the test database contains
the expected data for Customers and Products.
"""

def verify_database_content(db):
    """
    Verify that the test database has the expected data:
    - Customers 表中，CustomerID 为 'CUST1' 的记录存在且 CompanyName 为 "Tech Solutions"
    - Products 表中，ProductName 为 'Wireless Mouse' 的记录存在且 UnitPrice 为 25.99
    """
    # 检查 Customers 表
    customer = db.execute(
        "SELECT * FROM Customers WHERE CustomerID = 'CUST1'"
    ).fetchone()
    assert customer is not None, "Customer CUST1 should exist"
    assert customer["CompanyName"] == "Tech Solutions", "CompanyName must be 'Tech Solutions'"

    # 检查 Products 表
    product = db.execute(
        "SELECT * FROM Products WHERE ProductName = 'Wireless Mouse'"
    ).fetchone()
    assert product is not None, "Product 'Wireless Mouse' should exist"
    assert product["UnitPrice"] == 25.99, "UnitPrice must be 25.99"
