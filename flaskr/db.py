"""
Database module for managing SQLite connections and initialization.

This module provides functions to establish a database connection,
close connections, and initialize the required tables in `northwind.db`.
"""

import sqlite3
from typing import Any

from flask import g, current_app


def get_db() -> sqlite3.Connection:
    """
    Get the SQLite database connection, ensuring it reads from `app.config['DATABASE']`.

    Returns:
        sqlite3.Connection: The SQLite database connection.
    """
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db() -> None:
    """
    Close the database connection if it exists.

    This function is registered with Flask's `teardown_appcontext` to ensure
    the database connection is properly closed after each request.
    """
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_app(app: Any) -> None:
    """
    Register database-related functions with the Flask app.

    This ensures that `close_db()` is called automatically when the application context ends.

    Args:
        app (Any): The Flask application instance.
    """
    app.teardown_appcontext(close_db)


def initialize_northwind() -> None:
    """
    Ensure the `northwind.db` database has the required tables.

    This function checks if the `Authentication` and `Shopping_cart` tables exist,
    and creates them if necessary. It also inserts a default employee entry.
    """
    db = get_db()

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS Authentication (
            UserID TEXT PRIMARY KEY,
            PasswordHash TEXT NOT NULL,
            SessionID TEXT
        );
        """
    )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS Products (
            ProductID INTEGER PRIMARY KEY,
            ProductName TEXT NOT NULL,
            UnitPrice REAL,
            UnitsInStock INTEGER
        );
        """
    )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS Shopping_cart (
            ShopperID INTEGER NOT NULL,
            ProductID INTEGER NOT NULL,
            Quantity INTEGER NOT NULL DEFAULT 1,
            AddedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ProductID) REFERENCES Products(ProductID),
            PRIMARY KEY (ShopperID, ProductID)
        );
        """
    )

    db.execute(
        """
        INSERT INTO Employees (EmployeeID, LastName, FirstName)
        SELECT 999999, 'WEB', 'WEB'
        WHERE NOT EXISTS (
            SELECT 1 FROM Employees WHERE EmployeeID = 999999
        );
        """
    )

    db.commit()
