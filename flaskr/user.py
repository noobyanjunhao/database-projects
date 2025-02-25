import functools
import uuid
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)
from werkzeug.wrappers import Response as WerkzeugResponse
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db
from typing import Union, Optional, Callable, Any, Dict, TypeVar, cast

bp = Blueprint('user', __name__, url_prefix='/user')

F = TypeVar('F', bound=Callable[..., Any])

@bp.route('/register', methods=('GET', 'POST'))
def register() -> Union[str, WerkzeugResponse]:
    # Get the prefilled username if provided (from a login redirect)
    prefill_username: str = request.args.get('username', '')
    if request.method == 'POST':
        # Use the username from the form, falling back to the prefill if necessary.
        username: str = request.form.get('username', prefill_username).strip().upper()
        password: str = request.form['password']
        db = get_db()
        error: Optional[str] = None

        # ENFORCE EXACTLY 5 CHARACTERS
        if not username:
            error = 'User ID is required.'
        elif len(username) != 5:  # <-- Added line
            error = 'User ID must be exactly 5 characters.'  # <-- Added line
        elif not password:
            error = 'Password is required.'

        if error is None:
            # Check if the user exists in the Customers table.
            customer = db.execute(
                'SELECT * FROM Customers WHERE CustomerID = ?',
                (username,)
            ).fetchone()

            if customer is None:
                # If no customer exists, create a new row in Customers with the CustomerID.
                db.execute(
                    'INSERT INTO Customers (CustomerID) VALUES (?)',
                    (username,)
                )
            try:
                # Insert the authentication record.
                db.execute(
                    "INSERT INTO Authentication (UserID, PasswordHash, SessionID) VALUES (?, ?, ?)",
                    (username, generate_password_hash(password), session.get('session_id')),
                )
                db.commit()
            except db.IntegrityError:
                db.rollback()
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("user.login"))

        flash(error)

    return render_template('user/register.html', prefill_username=prefill_username)


@bp.route('/login', methods=('GET', 'POST'))
def login() -> Union[str, WerkzeugResponse]:
    if request.method == 'POST':
        # Convert username to uppercase so the lookup is case-insensitive.
        username: str = request.form['username'].strip().upper()
        password: str = request.form['password']
        db = get_db()
        error: Optional[str] = None

        # ENFORCE EXACTLY 5 CHARACTERS
        if not username:
            error = "User ID is required."
        elif len(username) != 5:  # <-- Added line
            error = "User ID must be exactly 5 characters."  # <-- Added line
        elif not password:
            error = "Password is required."
        
        if error is None:
            # Look up the user by UserID (which is stored in uppercase) in the Authentication table.
            user = db.execute(
                'SELECT * FROM Authentication WHERE UserID = ?',
                (username,)
            ).fetchone()

            if user is None:
                # If not found in Authentication, check the Customers table.
                customer = db.execute(
                    'SELECT * FROM Customers WHERE CustomerID = ?',
                    (username,)
                ).fetchone()
                if customer is not None:
                    flash("Username exists but has not finished registering, please create a password and register.")
                    # Redirect to register page with the username prefilled.
                    return redirect(url_for("user.register", username=username))
                else:
                    error = "Username not found, please make sure username is correct or register."
            elif not check_password_hash(user['PasswordHash'], password):
                error = "Password incorrect, please try again."

        if error is None:
            # Credentials are valid.
            old_session_id: Optional[str] = user['SessionID']
            new_session_id: str = session['session_id']
            session['user_id'] = username

            if old_session_id != new_session_id:
                db.execute(
                    'UPDATE Shopping_cart SET ShopperID = ? WHERE ShopperID = ?',
                    (new_session_id, old_session_id)
                )
                db.execute(
                    'UPDATE Authentication SET SessionID = ? WHERE UserID = ?',
                    (new_session_id, username)
                )
            db.commit()
            return redirect(url_for('products.list_products'))

        flash(error)

    return render_template('user/login.html')


@bp.before_app_request
def load_logged_in_user() -> None:
    user_id: Optional[str] = session.get('user_id')
    session_id: Optional[str] = session.get('session_id')
    if user_id is None or session_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM Authentication WHERE UserID = ? AND SessionID = ?',
            (user_id, session_id)
        ).fetchone()


@bp.route('/logout')
def logout() -> WerkzeugResponse:
    # Clear the entire Flask session
    session.clear()
    import secrets
    session['session_id'] = secrets.token_hex(16)
    
    # Redirect to the home page (or wherever you want after logout)
    return redirect(url_for('products.list_products'))


