"""Module tests for checkout functionality.

This module tests various checkout scenarios, including authentication, empty cart,
invalid sessions, database errors, and order storage.
"""

from typing import Any

import pytest
from flaskr.db import get_db


@pytest.fixture
def auth_actions(client: Any) -> Any:
    """
    Fixture that returns an instance of AuthActions for performing authentication actions.
    """
    class AuthActions:
        """Helper class for performing authentication actions in tests."""
        def login(self, username: str, password: str) -> Any:
            """
            Log in with the provided username and password.
            """
            return client.post("/user/login", data={"username": username, "password": password})

        def logout(self) -> Any:
            """
            Log out the current user.
            """
            return client.get("/user/logout")

    return AuthActions()


def test_checkout_requires_login(client: Any, auth_actions: Any, app: Any) -> None:
    """Ensure users must be logged in to access the checkout page."""
    response = client.get("/checkout/")
    assert response.status_code == 302
    assert response.headers["Location"] == "/user/login"

    client.post("/user/register", data={"username": "NEWUS", "password": "newpassword"})
    response = auth_actions.login("NEWUS", "newpassword")
    assert response.status_code == 302
    assert response.headers["Location"] == "/products"


def test_checkout_empty_cart(client: Any, auth_actions: Any) -> None:
    """Ensure users cannot checkout with an empty cart."""
    client.post("/user/register", data={"username": "NEWUS", "password": "newpassword"})
    auth_actions.login("NEWUS", "newpassword")
    response = client.get("/checkout/")
    assert response.status_code == 302
    assert response.headers["Location"] == "/cart/"


def test_checkout_invalid_session(client: Any, auth_actions: Any) -> None:
    """Ensure users with invalid session are redirected to the login page."""
    auth_actions.login("NEWUS", "newpassword")
    with client.session_transaction() as sess:
        sess["session_id"] = "fake-session-xyz"
    response = client.get("/checkout/")
    assert response.status_code == 302
    assert response.headers["Location"] == "/user/login"


def test_checkout_database_error(client: Any, auth_actions: Any, app: Any) -> None:
    """Ensure database errors during checkout are handled correctly."""
    client.post("/user/register", data={"username": "NEWUS", "password": "newpassword"})
    auth_actions.login("NEWUS", "newpassword")
    client.post("/cart/add/", data={"product_id": "42", "quantity": "2"})

    with app.app_context():
        db = get_db()
        db.execute("DROP TABLE Orders")  # Induce a DB error
        db.commit()

    response = client.post("/checkout/", data={
        "ship_name": "John Doe",
        "ship_address": "123 Main St",
        "ship_city": "Anytown",
        "ship_country": "USA",
        "place_order": "true"
    })
    assert response.status_code == 302
    assert response.headers["Location"] == "/cart/"


def test_checkout_get_request(client: Any, auth_actions: Any) -> None:
    """Ensure GET requests to the checkout page return the correct template."""
    client.post("/user/register", data={"username": "NEWUS", "password": "newpassword"})
    auth_actions.login("NEWUS", "newpassword")
    client.post("/cart/add/", data={"product_id": "1", "quantity": "1"})
    response = client.get("/checkout/")
    assert response.status_code == 200
    assert b"Checkout" in response.data


def test_successful_checkout_clears_cart(client: Any, auth_actions: Any, app: Any) -> None:
    """Ensure that a successful checkout clears the cart."""
    client.post("/user/register", data={"username": "NEWUS", "password": "newpassword"})
    auth_actions.login("NEWUS", "newpassword")
    client.post("/cart/add/", data={"product_id": "1", "quantity": "1"})
    response = client.post("/checkout/", data={
        "ship_name": "John Doe",
        "ship_address": "123 Main St",
        "ship_city": "Anytown",
        "ship_country": "USA",
        "place_order": "true"
    })
    assert response.status_code == 302
    assert response.headers["Location"] == "/orders/"

    with client.session_transaction() as sess:
        session_id = sess["session_id"]

    with app.app_context():
        db = get_db()
        cart_count = db.execute(
            "SELECT COUNT(*) FROM Shopping_cart WHERE ShopperID = ?",
            (session_id,)
        ).fetchone()[0]
        assert cart_count == 0


def test_order_is_correctly_stored(client: Any, auth_actions: Any, app: Any) -> None:
    """Ensure that order details are correctly stored in the database."""
    client.post("/user/register", data={"username": "NEWUS", "password": "newpassword"})
    auth_actions.login("NEWUS", "newpassword")
    client.post("/cart/add/", data={"product_id": "1", "quantity": "1"})
    response = client.post("/checkout/", data={
        "ship_name": "John Doe",
        "ship_address": "123 Main St",
        "ship_city": "Anytown",
        "ship_country": "USA",
        "place_order": "true"
    })
    assert response.status_code == 302
    assert response.headers["Location"] == "/orders/"

    with app.app_context():
        db = get_db()
        order = db.execute(
            "SELECT * FROM Orders WHERE CustomerID = ?",
            ("NEWUS",)
        ).fetchone()
        assert order is not None
        assert order["ShipName"] == "John Doe"
        assert order["ShipAddress"] == "123 Main St"
        assert order["ShipCity"] == "Anytown"
        assert order["ShipCountry"] == "USA"


def test_checkout_with_different_shipping_options(client: Any, auth_actions: Any, app: Any) -> None:
    """Ensure different shipping options are correctly stored."""
    client.post("/user/register", data={"username": "NEWUS", "password": "newpassword"})
    auth_actions.login("NEWUS", "newpassword")
    client.post("/cart/add/", data={"product_id": "1", "quantity": "1"})
    response = client.post("/checkout/", data={
        "ship_name": "Alice Smith",
        "ship_address": "456 Elm St",
        "ship_city": "Smalltown",
        "ship_region": "CA",
        "ship_postal_code": "12345",
        "ship_country": "USA",
        "ship_via": "2",
        "place_order": "true"
    })
    assert response.status_code == 302
    assert response.headers["Location"] == "/orders/"

    with app.app_context():
        db = get_db()
        order = db.execute(
            "SELECT * FROM Orders WHERE CustomerID = ?",
            ("NEWUS",)
        ).fetchone()
        assert order is not None
        assert order["ShipName"] == "Alice Smith"
        assert order["ShipAddress"] == "456 Elm St"
        assert order["ShipCity"] == "Smalltown"
        assert order["ShipRegion"] == "CA"
        assert order["ShipPostalCode"] == "12345"
        assert order["ShipCountry"] == "USA"
        assert order["ShipVia"] == 2


def test_multiple_users_checkout_separately(client: Any, auth_actions: Any, app: Any) -> None:
    """Ensure multiple users can checkout independently without conflicts."""
    client.post("/user/register", data={"username": "USER1", "password": "pass1"})
    auth_actions.login("USER1", "pass1")
    client.post("/cart/add/", data={"product_id": "1", "quantity": "2"})

    client.post("/user/register", data={"username": "USER2", "password": "pass2"})
    auth_actions.login("USER2", "pass2")
    client.post("/cart/add/", data={"product_id": "2", "quantity": "1"})

    response1 = client.post("/checkout/", data={
        "ship_name": "User One",
        "ship_address": "111 First St",
        "ship_city": "CityA",
        "ship_country": "USA",
        "place_order": "true"
    })
    response2 = client.post("/checkout/", data={
        "ship_name": "User Two",
        "ship_address": "222 Second St",
        "ship_city": "CityB",
        "ship_country": "Canada",
        "place_order": "true"
    })

    assert response1.status_code == 302
    assert response2.status_code == 302


def test_checkout_no_place_order(client: Any, auth_actions: Any, app: Any) -> None:
    """
    Test the code path where the user does not provide 'place_order',
    which should trigger the fallback returning a redirect to the cart page.
    """
    client.post("/user/register", data={"username": "NEWUS", "password": "newpassword"})
    auth_actions.login("NEWUS", "newpassword")
    client.post("/cart/add/", data={"product_id": "1", "quantity": "1"})
    response = client.post("/checkout/", data={
        "ship_name": "No Order",
        "ship_address": "111 AAA St",
        "ship_city": "CityX",
        "ship_country": "USA"
    })
    assert response.status_code == 302
    assert response.headers["Location"] == "/cart/"


def test_checkout_missing_employee(client: Any, auth_actions: Any, app: Any) -> None:
    """
    Test the scenario when the 'WEB' employee record is missing.
    The code should handle the exception and redirect to the cart page.
    """
    with app.app_context():
        db = get_db()
        db.execute("DELETE FROM Employees WHERE EmployeeID = 999999 AND LastName = 'WEB'")
        db.commit()

    client.post("/user/register", data={"username": "NEWUS", "password": "newpassword"})
    auth_actions.login("NEWUS", "newpassword")
    client.post("/cart/add/", data={"product_id": "1", "quantity": "1"})
    response = client.post("/checkout/", data={
        "ship_name": "John Missing",
        "ship_address": "123 NoEmployee Rd",
        "ship_city": "Nowhere",
        "ship_country": "USA",
        "place_order": "true"
    })
    assert response.status_code == 302
    assert response.headers["Location"] == "/cart/"


def test_checkout_no_cart_found_alt(client: Any, auth_actions: Any) -> None:
    """
    Alternative approach to trigger the case where cart_id is missing,
    ensuring user_id remains in session but session_id is None.
    """
    client.post("/user/register", data={"username": "ALTUSER", "password": "altpass"})
    auth_actions.login("ALTUSER", "altpass")
    with client.session_transaction() as sess:
        sess["user_id"] = "ALTUSER"
        sess["session_id"] = None
    response = client.get("/checkout/")
    assert response.status_code == 302
    assert response.headers["Location"] == "/cart/"


def test_checkout_post_no_user_in_session(client: Any, auth_actions: Any) -> None:
    """
    If request.method == 'POST' but no user_id or session_id exists in session,
    the user should be redirected to the login page.
    """
    client.post("/user/register", data={"username": "NOUSER", "password": "pass123"})
    auth_actions.login("NOUSER", "pass123")
    with client.session_transaction() as sess:
        sess.pop("user_id", None)
        sess.pop("session_id", None)
    response = client.post("/checkout/", data={
        "ship_name": "NoUser",
        "ship_address": "999 Nowhere",
        "ship_city": "Invisible",
        "ship_country": "USA",
        "place_order": "true"
    })
    assert response.status_code == 302
    assert response.headers["Location"] == "/user/login"


def test_checkout_post_user_not_in_db(client: Any, auth_actions: Any, app: Any) -> None:
    """
    If user_id/session_id exist in session but there is no corresponding user in the database,
    the code should redirect to the login page.
    """
    client.post("/user/register", data={"username": "MISSINGUSER", "password": "pass456"})
    auth_actions.login("MISSINGUSER", "pass456")
    with app.app_context():
        db = get_db()
        db.execute("DELETE FROM Authentication WHERE UserID = ?", ("MISSINGUSER",))
        db.commit()
    with client.session_transaction() as sess:
        pass
    response = client.post("/checkout/", data={
        "ship_name": "Missing DB",
        "ship_address": "101 Ghost Ln",
        "ship_city": "Nonexistent",
        "ship_country": "USA",
        "place_order": "true"
    })
    assert response.status_code == 302
    assert response.headers["Location"] == "/user/login"
