"""
Flask application initialization module.

This module creates the Flask app instance and registers all blueprints.
"""

import os
import secrets
from typing import Optional, Dict, Any

from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy

from flaskr.db import get_db, initialize_northwind
from flaskr.products import products_bp
from flaskr.user import bp as user_bp
from flaskr.cart import cart_bp
from flaskr.orders import orders_bp
from flaskr.landing import landing_bp
from flaskr.checkout import checkout_bp

db = SQLAlchemy()


def create_app(test_config: Optional[Dict[str, Any]] = None) -> Flask:
    """
    Create and configure a Flask application.

    Args:
        test_config (Optional[Dict[str, Any]]): Configuration dictionary for testing.

    Returns:
        Flask: A fully configured Flask application instance.
    """
    app = Flask(__name__, instance_relative_config=True)

    db_path = "northwind.db"

    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", os.urandom(24).hex()),
        DATABASE=db_path if test_config is None else test_config["DATABASE"],
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{db_path}",
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    with app.app_context():
        initialize_northwind()

    @app.before_request
    def ensure_session_id() -> None:
        """Ensure session_id exists before each request, or create one."""
        if "session_id" not in session:
            session["session_id"] = secrets.token_hex(16)

    @app.route("/hello")
    def hello() -> str:
        """Simple test route."""
        return "Hello, World!"

    db.init_app(app)

    app.register_blueprint(products_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(landing_bp)
    app.register_blueprint(checkout_bp)

    return app
