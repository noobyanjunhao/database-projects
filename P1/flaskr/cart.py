"""
Cart module for managing shopping cart functionality.

This module includes routes for viewing, adding, and removing items
in the shopper's cart, as well as auxiliary functions such as
cleanup and timestamp handling.
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

from flask import Blueprint, request, session, redirect, url_for, render_template
from werkzeug.wrappers import Response as WerkzeugResponse

from flaskr.db import get_db

cart_bp = Blueprint("cart", __name__, url_prefix="/cart")


@cart_bp.route("/")
def view_cart() -> str:
    """
    Show all items in this shopper's cart, including product details.

    Returns:
        str: Rendered template with items in the cart.
    """
    cart_id: str = session["session_id"]
    db = get_db()

    rows = db.execute(
        """
        SELECT sc.ProductID, sc.Quantity, sc.AddedAt,
               p.ProductName, p.UnitPrice
        FROM Shopping_cart sc
        JOIN Products p ON sc.ProductID = p.ProductID
        WHERE sc.ShopperID = ?
        """,
        (cart_id,),
    ).fetchall()

    items: List[Dict[str, Any]] = []
    total: float = 0.0
    for row in rows:
        item_total: float = row["UnitPrice"] * row["Quantity"]
        total += item_total
        items.append(
            {
                "product_id": row["ProductID"],
                "name": row["ProductName"],
                "price": row["UnitPrice"],
                "quantity": row["Quantity"],
                "timestamp": row["AddedAt"],
                "total_price": item_total,
            }
        )

    return render_template("cart/cart_html.html", items=items, total=total)


@cart_bp.route("add/", methods=["POST"])
def add_to_cart() -> Tuple[Dict[str, str], int]:
    """
    Add a product to the cart, or increase quantity if it already exists.

    Returns:
        Tuple[Dict[str, str], int]: A JSON status message and HTTP code.
    """
    cart_id: str = session["session_id"]
    product_id: str = request.form["product_id"]
    added_quantity: int = int(
        request.form.get("quantity", 1)
    )  # Default to 1 if missing

    db = get_db()

    existing_item: Optional[sqlite3.Row] = db.execute(
        """
        SELECT Quantity FROM Shopping_cart
        WHERE ShopperID = ? AND ProductID = ?
        """,
        (cart_id, product_id),
    ).fetchone()

    if existing_item:
        new_quantity: int = existing_item["Quantity"] + added_quantity
        db.execute(
            """
            UPDATE Shopping_cart
            SET Quantity = ?, AddedAt = CURRENT_TIMESTAMP
            WHERE ShopperID = ? AND ProductID = ?
            """,
            (new_quantity, cart_id, product_id),
        )
    else:
        db.execute(
            """
            INSERT INTO Shopping_cart (ShopperID, ProductID, Quantity, AddedAt)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (cart_id, product_id, added_quantity),
        )

    db.commit()
    return {"status": "success", "message": "Item added to cart"}, 200


@cart_bp.route("remove/", methods=["POST"])
def remove_from_cart() -> WerkzeugResponse:
    """
    Remove a single product from the cart by its ProductID.

    Returns:
        WerkzeugResponse: A redirect to the cart view.
    """
    if "session_id" not in session:
        return redirect(url_for("cart.view_cart"))

    cart_id: str = session["session_id"]
    product_id: str = request.form["product_id"]

    db = get_db()
    db.execute(
        """
        DELETE FROM Shopping_cart
        WHERE ProductID = ? AND ShopperID = ?
        """,
        (product_id, cart_id),
    )
    db.commit()

    return redirect(url_for("cart.view_cart"))


def get_est_time() -> datetime:
    """
    Return the current time (EST or local time, as needed).

    Returns:
        datetime: Current local time.
    """
    return datetime.now()


def cleanup_old_cart_entries() -> None:
    """
    Remove cart entries older than 30 days.
    """
    db = get_db()
    one_month_ago: datetime = get_est_time() - timedelta(days=30)
    db.execute(
        """
        DELETE FROM Shopping_cart
        WHERE AddedAt < ?
        """,
        (one_month_ago,),
    )
    db.commit()
