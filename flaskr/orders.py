"""
Orders module for displaying current user orders.

This module fetches all orders for the logged-in user and displays them in a template.
"""

from typing import Union, List, Dict, Any

from flask import Blueprint, render_template, session, redirect, url_for
from werkzeug.wrappers import Response as WerkzeugResponse

from flaskr.db import get_db


orders_bp = Blueprint("orders", __name__, url_prefix="/orders")


@orders_bp.route("/")
def view_orders() -> Union[str, WerkzeugResponse]:
    """
    Display all orders for the currently logged-in user.
    If user is not logged in, redirect to login page.
    """
    if "user_id" not in session:
        return redirect(url_for("user.login"))

    user_id: str = session["user_id"]
    db = get_db()

    orders = db.execute(
        """
        SELECT * FROM Orders WHERE CustomerID = ?
        ORDER BY OrderDate DESC
    """,
        (user_id,),
    ).fetchall()

    orders_list: List[Dict[str, Any]] = [dict(order) for order in orders]

    return render_template("orders/orders.html", orders=orders_list)
