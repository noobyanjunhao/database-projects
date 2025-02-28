# pylint: disable=no-else-return
"""
User authentication module.

This module handles user registration, login, logout, and session management.
"""

import secrets
from typing import Union, Optional, Callable, Any, TypeVar

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.wrappers import Response as WerkzeugResponse
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

bp = Blueprint("user", __name__, url_prefix="/user")

F = TypeVar("F", bound=Callable[..., Any])


@bp.route("/register", methods=("GET", "POST"))
def register() -> Union[str, WerkzeugResponse]:
    """
    Handle user registration.

    - Validates input (username must be 5 characters).
    - Checks if the user exists in Customers.
    - If not registered, creates a new user in Authentication.
    """
    prefill_username: str = request.args.get("username", "")
    if request.method == "POST":
        username: str = request.form.get("username", prefill_username).strip().upper()
        password: str = request.form["password"]
        db = get_db()
        error: Optional[str] = None

        if not username:
            error = "User ID is required."
        elif len(username) != 5:
            error = "User ID must be exactly 5 characters."
        elif not password:
            error = "Password is required."

        if error is None:
            customer = db.execute(
                "SELECT * FROM Customers WHERE CustomerID = ?", (username,)
            ).fetchone()

            if customer is None:
                db.execute("INSERT INTO Customers (CustomerID) VALUES (?)", (username,))
            try:
                db.execute(
                    "INSERT INTO Authentication (UserID, PasswordHash, SessionID) VALUES (?, ?, ?)",
                    (
                        username,
                        generate_password_hash(password),
                        session.get("session_id"),
                    ),
                )
                db.commit()
            except db.IntegrityError:
                db.rollback()
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("user.login"))

        flash(error)

    return render_template("user/register.html", prefill_username=prefill_username)


@bp.route("/login", methods=("GET", "POST"))
def login() -> Union[str, WerkzeugResponse]:
    """
    Handle user login.

    - Checks if the user exists in Authentication.
    - If not, verifies if they exist in Customers.
    - If valid, updates session and redirects to products.
    """
    if request.method == "POST":
        username: str = request.form["username"].strip().upper()
        password: str = request.form["password"]
        db = get_db()
        error: Optional[str] = None

        if not username:
            error = "User ID is required."
        elif len(username) != 5:
            error = "User ID must be exactly 5 characters."
        elif not password:
            error = "Password is required."

        if error is None:
            user = db.execute(
                "SELECT * FROM Authentication WHERE UserID = ?", (username,)
            ).fetchone()

            if user is None:
                customer = db.execute(
                    "SELECT * FROM Customers WHERE CustomerID = ?", (username,)
                ).fetchone()
                if customer is not None:
                    flash("Username exists but has not finished registering.")
                    return redirect(url_for("user.register", username=username))
                else:
                    error = "Username not found, please register."
            elif not check_password_hash(user["PasswordHash"], password):
                error = "Password incorrect."

        if error is None:
            old_session_id: Optional[str] = user["SessionID"]
            new_session_id: str = session["session_id"]
            session["user_id"] = username

            if old_session_id != new_session_id:
                db.execute(
                    "UPDATE Shopping_cart SET ShopperID = ? WHERE ShopperID = ?",
                    (new_session_id, old_session_id),
                )
                db.execute(
                    "UPDATE Authentication SET SessionID = ? WHERE UserID = ?",
                    (new_session_id, username),
                )
            db.commit()
            return redirect(url_for("products.list_products"))

        flash(error)

    return render_template("user/login.html")


@bp.before_app_request
def load_logged_in_user() -> None:
    """
    Load the currently logged-in user.

    Retrieves user authentication information from the session
    and stores it in `g.user` for request handling.
    """
    user_id: Optional[str] = session.get("user_id")
    session_id: Optional[str] = session.get("session_id")
    if user_id is None or session_id is None:
        g.user = None
    else:
        g.user = (
            get_db()
            .execute(
                "SELECT * FROM Authentication WHERE UserID = ? AND SessionID = ?",
                (user_id, session_id),
            )
            .fetchone()
        )


@bp.route("/logout")
def logout() -> WerkzeugResponse:
    """
    Log out the user by clearing the session and generating a new session ID.
    """
    session.clear()
    session["session_id"] = secrets.token_hex(16)
    return redirect(url_for("products.list_products"))
