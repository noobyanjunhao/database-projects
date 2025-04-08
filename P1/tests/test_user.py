"""Tests for user functionality."""

# pylint: disable=redefined-outer-name, unused-argument

from typing import Any

import pytest
from flask.testing import FlaskClient
from flask import Flask
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db


class AuthActions:
    """Helper class to perform authentication actions in tests."""

    def __init__(self, client: FlaskClient):
        self._client = client

    def login(self, username: str, password: str) -> Any:
        """Send a POST request to login with the given username and password."""
        return self._client.post(
            "/user/login", data={"username": username, "password": password}
        )

    def logout(self) -> Any:
        """Send a GET request to logout."""
        return self._client.get("/user/logout")


@pytest.fixture
def auth(client: FlaskClient) -> AuthActions:
    """Fixture to provide an instance of AuthActions."""
    return AuthActions(client)


def test_register(client: FlaskClient, app: Flask) -> None:
    """Test user registration page and registration logic."""
    response = client.get("/user/register")
    assert response.status_code == 200

    # Successful registration
    response = client.post(
        "/user/register", data={"username": "NEWUS", "password": "newpassword"}
    )
    assert response.status_code == 302
    assert response.headers["Location"] == "/user/login"

    # Validate in the database
    with app.app_context():
        db = get_db()
        user = db.execute(
            "SELECT * FROM Authentication WHERE UserID = 'NEWUS'"
        ).fetchone()
        assert user is not None
        assert check_password_hash(user["PasswordHash"], "newpassword")


def test_register_failures(client: FlaskClient) -> None:
    """Test failure cases for user registration."""
    # User ID too short
    response = client.post(
        "/user/register", data={"username": "AB", "password": "newpassword"}
    )
    assert b"User ID must be exactly 5 characters." in response.data

    # User ID is empty
    response = client.post(
        "/user/register", data={"username": "", "password": "newpassword"}
    )
    assert b"User ID is required." in response.data

    # Password is empty
    response = client.post("/user/register", data={"username": "ABCDE", "password": ""})
    assert b"Password is required." in response.data

    # User already exists
    client.post("/user/register", data={"username": "NEWUS", "password": "newpassword"})
    response = client.post(
        "/user/register", data={"username": "NEWUS", "password": "anotherpass"}
    )
    assert b"User NEWUS is already registered." in response.data


def test_login(client: FlaskClient, auth: AuthActions) -> None:
    """Test login with correct credentials."""
    client.post("/user/register", data={"username": "NEWUS", "password": "newpassword"})

    response = client.get("/user/login")
    assert response.status_code == 200

    # Correct login
    response = auth.login("NEWUS", "newpassword")
    assert response.status_code == 302
    assert response.headers["Location"] == "/products"

    # Ensure session is set correctly
    with client.session_transaction() as sess:
        assert sess["user_id"] == "NEWUS"


def test_login_failures(client: FlaskClient, auth: AuthActions) -> None:
    """Test login failures for non-existent user and wrong password."""
    # Non-existent user
    response = auth.login("FAKEU", "newpassword")
    assert b"Username not found" in response.data

    # Wrong password
    client.post("/user/register", data={"username": "NEWUS", "password": "newpassword"})
    response = auth.login("NEWUS", "wrongpassword")
    assert b"Password incorrect" in response.data


def test_logout(client: FlaskClient, auth: AuthActions) -> None:
    """Test logout functionality."""
    auth.login("NEWUS", "newpassword")
    response = client.get("/user/logout")
    assert response.headers["Location"] == "/products"


def test_login_no_username(client: FlaskClient, auth: AuthActions) -> None:
    """Test login with an empty username field."""
    response = auth.login("", "somepassword")
    assert response.status_code == 200
    assert b"User ID is required." in response.data


def test_login_wrong_length_username(client: FlaskClient, auth: AuthActions) -> None:
    """Test login with a username that is not exactly 5 characters."""
    response = auth.login("AB", "somepassword")  # Only 2 chars
    assert response.status_code == 200
    assert b"User ID must be exactly 5 characters." in response.data


def test_login_no_password(client: FlaskClient, auth: AuthActions) -> None:
    """Test login with an empty password field."""
    response = auth.login("ABCDE", "")
    assert response.status_code == 200
    assert b"Password is required." in response.data


def test_login_customer_not_finished_registering(client: FlaskClient, app: Flask) -> None:
    """Test login when user exists in Customers but not in Authentication."""
    with app.app_context():
        db = get_db()
        # Insert a customer row but no corresponding Authentication record.
        db.execute("INSERT INTO Customers (CustomerID) VALUES (?)", ("ABCDX",))
        db.commit()

    # Attempt to log in with the customer.
    # Use follow_redirects=True to follow the redirect to the registration page.
    response = client.post(
        "/user/login",
        data={"username": "ABCDX", "password": "somepassword"},
        follow_redirects=True,
    )
    # The final response should have a 200 status code.
    assert response.status_code == 200
    # The registration page should be rendered (e.g., it contains the registration form).
    assert b"register" in response.data.lower()
    # Verify that the flash message is present.
    assert b"Username exists but has not finished registering." in response.data


def test_login_with_different_session_ids(client: FlaskClient, app: Flask) -> None:
    """
    Test that the 'UPDATE Shopping_cart' and 'UPDATE Authentication' queries
    run when the user's old session ID doesn't match the current session ID.
    """
    old_session = "oldsession123"
    new_session = "newsession456"

    # 1) Insert a user into Authentication with a known old_session ID
    with app.app_context():
        db = get_db()
        db.execute(
            """
            INSERT INTO Authentication (UserID, PasswordHash, SessionID)
            VALUES (?, ?, ?)
            """,
            ("ABCDE", generate_password_hash("secret"), old_session),
        )
        db.commit()

    # 2) Force the test client's session to be new_session
    with client.session_transaction() as sess:
        sess["session_id"] = new_session

    # 3) Log in with the user "ABCDE" whose DB session is old_session
    response = client.post(
        "/user/login",
        data={"username": "ABCDE", "password": "secret"},
        follow_redirects=True,
    )
    # This should trigger the branch where old_session != new_session

    # 4) Assert that we indeed reach a successful page
    assert response.status_code == 200
    # Optionally check the final page content
    assert (
        b"products" in response.data.lower()
        or b"some known text" in response.data.lower()
    )

    # 5) Confirm the DB was updated with the new_session
    with app.app_context():
        db = get_db()
        row = db.execute(
            "SELECT SessionID FROM Authentication WHERE UserID = ?", ("ABCDE",)
        ).fetchone()
        assert row is not None
        assert row["SessionID"] == new_session
