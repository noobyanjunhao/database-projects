"""Main site views."""
from typing import Any

from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index() -> Any:
    """Render the homepage."""
    return render_template("index.html")


@main_bp.route("/dashboard")
def dashboard() -> Any:
    """Render the dashboard page."""
    return render_template("dashboard.html")
