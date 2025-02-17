from flask import Blueprint, request, session, redirect, url_for, render_template, flash
from flaskr.db import get_db
import secrets

cart_bp = Blueprint('cart', __name__, url_prefix = '/cart')
@cart_bp.route('/')
def view_cart():
    """Show all items in this shopper's cart."""
    if 'cart_id' not in session:
        # If no cart_id, create one 
        session['cart_id'] = secrets.token_hex(16)

    cart_id = session['cart_id']
    db = get_db()

    # Retrieve multiple rows for the same ShopperID
    rows = db.execute("""
        SELECT ID, ProductID, Quantity, AddedAt 
        FROM Shopping_cart 
        WHERE ShopperID = ?
    """, (cart_id,)).fetchall()

    items = []
    for row in rows:
        items.append({
            'id': row['ID'],  # Added 'id' to track each cart item uniquely
            'product_id': row['ProductID'],
            'quantity': row['Quantity'],
            'timestamp': row['AddedAt']
        })

    return render_template('cart/cart_html.html', items=items)

@cart_bp.route('add/', methods=['POST'])
def add_to_cart():
    """Add a new row to the cart for each 'Add' action."""
    if 'cart_id' not in session:
        session['cart_id'] = secrets.token_hex(16)
    
    cart_id = session['cart_id']
    product_id = request.form['product_id']
    quantity = int(request.form.get('quantity', 1))  # Default 1 if none provided
    
    db = get_db()
    # Simple INSERT (no OR REPLACE) => each add creates a separate row
    db.execute("""
        INSERT INTO Shopping_cart (ShopperID, ProductID, Quantity, AddedAt)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    """, (cart_id, product_id, quantity))
    db.commit()

    return redirect(url_for('cart.view_cart'))

@cart_bp.route('remove/', methods=['POST'])
def remove_from_cart():
    """Remove a single row from the cart by its ID."""
    if 'cart_id' not in session:
        return redirect(url_for('cart.view_cart'))

    cart_id = session['cart_id']
    row_id = request.form['row_id']  # We'll pass in the ID of the cart row to remove

    db = get_db()
    # Delete only the row that matches both the ID and the ShopperID
    db.execute("""
        DELETE FROM Shopping_cart 
        WHERE ID = ? AND ShopperID = ?
    """, (row_id, cart_id))
    db.commit()

    return redirect(url_for('cart.view_cart'))

@cart_bp.route('checkout/', methods=['GET', 'POST'])
def checkout():
    """Checkout the cart."""
    if request.method == 'POST':
        # Ensure the user is logged in by checking the session
        if 'user_id' not in session or 'session_id' not in session:
            # User is not logged in, redirect to login
            return redirect(url_for('user.login'))

        cart_id = session.get('cart_id')
        if not cart_id:
            # No cart found, redirect to cart view
            print("No cart found, redirect to cart view")
            return redirect(url_for('cart.view_cart'))

        db = get_db()

        # Check if user is logged in by retrieving user ID
        user_row = db.execute(
            "SELECT UserID FROM Authentication WHERE UserID = ? AND SessionID = ?",
            (session['user_id'], session['session_id'])
        ).fetchone()

        if not user_row:
            # User is not logged in, redirect to login
            return redirect(url_for('user.login'))

        user_id = user_row['UserID']

        # Check if the user wants to place an order

        if request.form.get('place_order'):
            
            ship_name = request.form['ship_name']
            ship_address = request.form['ship_address']
            ship_city = request.form['ship_city']
            ship_region = request.form.get('ship_region', '')
            ship_postal_code = request.form.get('ship_postal_code', '')
            ship_country = request.form['ship_country']
            ship_via = request.form.get('ship_via', 1)  # default to 1 for "Standard"

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

            order_id = cursor.lastrowid  # Get the OrderID from the inserted order

            try:
                # Clear the cart
                db.execute("DELETE FROM Shopping_Cart WHERE ShopperID = ?", (cart_id,))
                db.commit()

                # Clean up old cart entries
                db.execute("DELETE FROM Shopping_Cart WHERE AddedAt < datetime('now', '-1 month')")
                db.commit()

                flash("Order placed successfully, thank you!")

                return redirect(url_for('orders.view_orders'))
            except Exception as e:
                db.rollback()
                flash(f"An error occurred during checkout: {e}")
                return redirect(url_for('cart.view_cart'))
        else:
            # User decided not to place an order, redirect back to cart
            return redirect(url_for('cart.view_cart'))

    return render_template('cart/checkout.html')

