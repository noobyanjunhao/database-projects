from flask import Blueprint, request, session, redirect, url_for, render_template, flash
from flaskr.db import get_db

checkout_bp = Blueprint('checkout', __name__, url_prefix='/checkout')

@checkout_bp.route('/', methods=['GET', 'POST'])
def checkout():
    """Checkout the cart."""
    if 'user_id' not in session or 'session_id' not in session:
        return redirect(url_for('user.login'))
    
    cart_id = session.get('session_id')
    if not cart_id:
        print("No cart found, redirect to cart view")
        return redirect(url_for('cart.view_cart'))

    db = get_db()

    # Check if the cart is empty
    cart_items = db.execute("""
        SELECT COUNT(*) as count FROM Shopping_cart WHERE ShopperID = ?
    """, (cart_id,)).fetchone()

    if cart_items['count'] == 0:
        flash("Your shopping cart is empty. Please add items before checkout.", "danger")
        return redirect(url_for('cart.view_cart'))  # Empty cart, return to cart view
    
    if request.method == 'POST':
        # Double-check session (redundant, but safety check)
        if 'user_id' not in session or 'session_id' not in session:
            return redirect(url_for('user.login'))

        # Verify that the user is logged in using their session_id.
        user_row = db.execute(
            "SELECT UserID FROM Authentication WHERE UserID = ? AND SessionID = ?",
            (session['user_id'], session['session_id'])
        ).fetchone()

        if not user_row:
            return redirect(url_for('user.login'))

        user_id = user_row['UserID']

        if request.form.get('place_order'):
            ship_name = request.form['ship_name']
            ship_address = request.form['ship_address']
            ship_city = request.form['ship_city']
            ship_region = request.form.get('ship_region', '')
            ship_postal_code = request.form.get('ship_postal_code', '')
            ship_country = request.form['ship_country']
            ship_via = request.form.get('ship_via', 1)  # Default to 1 for "Standard"

            try:
                # Attempt to insert the order.
                cursor = db.execute("""
                    INSERT INTO Orders (
                        CustomerID, EmployeeID, OrderDate, RequiredDate, ShippedDate, 
                        ShipVia, Freight, ShipName, ShipAddress, ShipCity, 
                        ShipRegion, ShipPostalCode, ShipCountry
                    )
                    VALUES (?, ?, CURRENT_TIMESTAMP, NULL, NULL, ?, 0, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id, 999999, ship_via, ship_name, ship_address, 
                    ship_city, ship_region, ship_postal_code, ship_country
                ))
                db.commit()
                order_id = cursor.lastrowid

            except Exception as e:
                db.rollback()
                flash(f"An error occurred during order placement: {e}", "danger")
                return redirect(url_for('cart.view_cart'))

            try:
                # Clear all cart items for this session_id.
                db.execute("DELETE FROM Shopping_cart WHERE ShopperID = ?", (cart_id,))
                db.commit()

                # Optionally, remove stale cart entries (older than 1 month)
                db.execute("DELETE FROM Shopping_cart WHERE AddedAt < datetime('now', '-1 month')")
                db.commit()

                flash("Order placed successfully, thank you!")
                return redirect(url_for('orders.view_orders'))
            except Exception as e:
                db.rollback()
                flash(f"An error occurred while clearing your cart: {e}", "danger")
                return redirect(url_for('cart.view_cart'))
        else:
            return redirect(url_for('cart.view_cart'))

    return render_template('cart/checkout.html')
