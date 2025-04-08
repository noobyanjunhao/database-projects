"""Tests for orders functionality."""

from typing import Callable

from flask import Flask
from flask.testing import FlaskClient

from flaskr.db import get_db


def test_view_orders_requires_login(client: FlaskClient) -> None:
    """Test that viewing orders redirects to login if user is not authenticated"""
    response = client.get("/orders/")
    assert response.status_code == 302  # Expect redirect
    assert response.headers["Location"] == "/user/login"


def test_view_orders_empty(
    client: FlaskClient, auth: Callable[[str, str], None]
) -> None:
    """Test viewing orders when user has no orders"""
    # Set session_id before registering so it's used during registration.
    with client.session_transaction() as sess:
        sess["session_id"] = "test-session-123"

    # Register and then log in the user.
    client.post("/user/register", data={"username": "NEWUS", "password": "testpass"})
    auth("NEWUS", "testpass")

    response = client.get("/orders/")
    assert response.status_code == 200
    assert b"You have no orders yet" in response.data


def test_order_creation_after_checkout(client: FlaskClient, app: Flask) -> None:
    """Test that orders are created properly after checkout"""
    # Set session id before registration so the same value is used during registration.
    with client.session_transaction() as sess:
        sess["session_id"] = "test-session-123"

    # Register the new user; registration will use the session_id we set above.
    client.post("/user/register", data={"username": "NEWUS", "password": "testpass"})

    # Now set user_id in the session so the app recognizes the user as logged in.
    with client.session_transaction() as sess:
        sess["user_id"] = "NEWUS"

    # Add item to cart
    client.post("/cart/add/", data={"product_id": "1", "quantity": "2"})

    # Perform checkout
    checkout_data = {
        "ship_name": "John Doe",
        "ship_address": "123 Test St",
        "ship_city": "Test City",
        "ship_country": "Test Country",
        "ship_via": "1",
        "place_order": "true",
    }

    response = client.post("/checkout/", data=checkout_data)
    assert response.status_code == 302
    assert response.headers["Location"] == "/orders/"

    # Verify order in database
    with app.app_context():
        db = get_db()
        order = db.execute("SELECT * FROM Orders WHERE CustomerID = 'NEWUS'").fetchone()

        assert order is not None
        assert order["ShipName"] == "John Doe"
        assert order["ShipAddress"] == "123 Test St"
        assert order["ShipCity"] == "Test City"
        assert order["ShipCountry"] == "Test Country"
        assert order["ShipVia"] == 1
        assert order["EmployeeID"] == 999999  # The WEB employee ID


def test_multiple_orders_display(client: FlaskClient, app: Flask) -> None:
    """Test that multiple orders are displayed correctly"""
    # Register and login
    client.post("/user/register", data={"username": "NEWUS", "password": "testpass"})
    with client.session_transaction() as sess:
        sess["session_id"] = "test-session-123"
        sess["user_id"] = "NEWUS"

    # Create two orders directly in the database
    with app.app_context():
        db = get_db()
        db.execute(
            """
            INSERT INTO Orders (
                CustomerID, EmployeeID, OrderDate, RequiredDate,
                ShipVia, ShipName, ShipAddress, ShipCity, ShipCountry
            ) VALUES 
            (?, 999999, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1, ?, ?, ?, ?),
            (?, 999999, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 2, ?, ?, ?, ?)
            """,
            (
                "NEWUS",
                "Test User 1",
                "Address 1",
                "City 1",
                "Country 1",
                "NEWUS",
                "Test User 2",
                "Address 2",
                "City 2",
                "Country 2",
            ),
        )
        db.commit()

    # View orders
    response = client.get("/orders/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    # Check both orders are displayed
    assert "Test User 1" in html
    assert "Test User 2" in html
    assert "Address 1" in html
    assert "Address 2" in html
    assert "Standard" in html  # ShipVia = 1
    assert "Express" in html  # ShipVia = 2


def test_cart_cleared_after_order(client: FlaskClient, app: Flask) -> None:
    """Test that the shopping cart is cleared after successful order placement"""
    # Set the session_id before registration so that it is used during registration.
    with client.session_transaction() as sess:
        sess["session_id"] = "test-session-123"

    # Register the new user; the registration route will pick up the session_id.
    client.post("/user/register", data={"username": "NEWUS", "password": "testpass"})

    # Now, set user_id in session so that the app recognizes the user as logged in.
    with client.session_transaction() as sess:
        sess["user_id"] = "NEWUS"

    # Add item to cart
    client.post("/cart/add/", data={"product_id": "1", "quantity": "2"})

    # Perform checkout
    checkout_data = {
        "ship_name": "John Doe",
        "ship_address": "123 Test St",
        "ship_city": "Test City",
        "ship_country": "Test Country",
        "ship_via": "1",
        "place_order": "true",
    }

    response = client.post("/checkout/", data=checkout_data)
    assert response.status_code == 302
    assert response.headers["Location"] == "/orders/"

    # Optionally, verify that the cart is cleared in the database.
    with app.app_context():
        db = get_db()
        cart_items = db.execute(
            "SELECT * FROM Shopping_cart WHERE ShopperID = ?", ("test-session-123",)
        ).fetchall()
        assert len(cart_items) == 0
