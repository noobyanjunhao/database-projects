# pylint: disable=too-many-locals, too-many-return-statements, broad-exception-caught
"""
Checkout module for handling the cart checkout process.

This module manages the checkout flow, including verifying user session,
checking cart contents, placing orders, and clearing cart entries.
"""

from typing import Union, Any

from flask import (
    Blueprint,
    request,
    session,
    redirect,
    url_for,
    render_template,
    flash,
    Response as FlaskResponse,
)
from werkzeug.wrappers import Response as WerkzeugResponse

from flaskr.db import get_db

checkout_bp = Blueprint("checkout", __name__, url_prefix="/checkout")


@checkout_bp.route("/", methods=["GET", "POST"])
def checkout() -> Union[str, FlaskResponse, WerkzeugResponse]:
    """
    Handle the checkout process.

    - Ensures user is logged in and cart is not empty.
    - On POST, attempts to place the order and clear the cart.
    """
    if "user_id" not in session or "session_id" not in session:
        return redirect(url_for("user.login"))

    cart_id: Any = session.get("session_id")
    if not cart_id:
        print("No cart found, redirecting to cart view.")
        return redirect(url_for("cart.view_cart"))

    db = get_db()

    cart_items = db.execute(
        """
        SELECT COUNT(*) as count 
        FROM Shopping_cart 
        WHERE ShopperID = ?
        """,
        (cart_id,),
    ).fetchone()

    if cart_items["count"] == 0:
        flash(
            "Your shopping cart is empty. Please add items before checkout.", "danger"
        )
        return redirect(url_for("cart.view_cart"))

    if request.method == "POST":
        if "user_id" not in session or "session_id" not in session:
            return redirect(url_for("user.login"))

        user_row = db.execute(
            "SELECT UserID FROM Authentication WHERE UserID = ? AND SessionID = ?",
            (session["user_id"], session["session_id"]),
        ).fetchone()

        if not user_row:
            return redirect(url_for("user.login"))

        user_id: str = user_row["UserID"]

        if request.form.get("place_order"):
            ship_name: str = request.form["ship_name"]
            ship_address: str = request.form["ship_address"]
            ship_city: str = request.form["ship_city"]
            ship_region: str = request.form.get("ship_region", "")
            ship_postal_code: str = request.form.get("ship_postal_code", "")
            ship_country: str = request.form["ship_country"]
            ship_via: int = int(request.form.get("ship_via", 1))

            try:
                employee = db.execute(
                    """
                    SELECT EmployeeID 
                    FROM Employees 
                    WHERE LastName = 'WEB' AND EmployeeID = 999999
                    """
                ).fetchone()

                employee_id = employee["EmployeeID"]

                cursor = db.execute(
                    """
                    INSERT INTO Orders (
                        CustomerID, EmployeeID, OrderDate, RequiredDate, 
                        ShippedDate, ShipVia, Freight, ShipName, 
                        ShipAddress, ShipCity, ShipRegion, 
                        ShipPostalCode, ShipCountry
                    )
                    VALUES (
                        ?, ?, CURRENT_TIMESTAMP, NULL, NULL, ?, 0, ?, 
                        ?, ?, ?, ?, ?
                    )
                    """,
                    (
                        user_id,
                        employee_id,
                        ship_via,
                        ship_name,
                        ship_address,
                        ship_city,
                        ship_region,
                        ship_postal_code,
                        ship_country,
                    ),
                )
                db.commit()

                order_id: Any = cursor.lastrowid  # pylint: disable=unused-variable
            except Exception as e:
                db.rollback()
                flash(f"An error occurred during order placement: {e}", "danger")
                return redirect(url_for("cart.view_cart"))

            try:

                db.execute("DELETE FROM Shopping_cart WHERE ShopperID = ?", (cart_id,))
                db.commit()

                db.execute(
                    "DELETE FROM Shopping_cart WHERE AddedAt < datetime('now', '-1 month')"
                )
                db.commit()

                flash("Order placed successfully, thank you!")
                return redirect(url_for("orders.view_orders"))
            except Exception as e:
                db.rollback()
                flash(f"An error occurred while clearing your cart: {e}", "danger")
                return redirect(url_for("cart.view_cart"))
        else:
            return redirect(url_for("cart.view_cart"))

    return render_template("cart/checkout.html")
