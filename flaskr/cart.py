from flask import Blueprint, request, session, redirect, url_for, render_template, flash
from flaskr.db import get_db

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')

@cart_bp.route('/')
def view_cart():
    """Show all items in this shopper's cart."""
    # Use the pre-created session_id (fallback to generating one if missing)
    
    cart_id = session['session_id']
    db = get_db()

    # Retrieve rows matching the session_id as the ShopperID.
    rows = db.execute("""
        SELECT ProductID, Quantity, AddedAt 
        FROM Shopping_cart 
        WHERE ShopperID = ?
    """, (cart_id,)).fetchall()

    items = []
    for row in rows:
        items.append({
            'product_id': row['ProductID'],
            'quantity': row['Quantity'],
            'timestamp': row['AddedAt']
        })

    return render_template('cart/cart_html.html', items=items)

@cart_bp.route('add/', methods=['POST'])
def add_to_cart():
    """Add a new row to the cart for each 'Add' action."""
    
    
    """Add a product to the cart, or increase the quantity if it already exists."""
    cart_id = session['session_id']
    product_id = request.form['product_id']
    added_quantity = int(request.form.get('quantity', 1))  # Default to 1 if not provided
    
    db = get_db()
    
    db = get_db()
    existing_item = db.execute("""
        SELECT Quantity FROM Shopping_cart 
        WHERE ShopperID = ? AND ProductID = ?
    """, (cart_id, product_id)).fetchone()
    
    if existing_item:
        # Increase the quantity by the added amount
        new_quantity = existing_item['Quantity'] + added_quantity
        db.execute("""
            UPDATE Shopping_cart 
            SET Quantity = ?, AddedAt = CURRENT_TIMESTAMP 
            WHERE ShopperID = ? AND ProductID = ?
        """, (new_quantity, cart_id, product_id))
    else:
        # Insert a new row for the product
        db.execute("""
            INSERT INTO Shopping_cart (ShopperID, ProductID, Quantity, AddedAt)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """, (cart_id, product_id, added_quantity))
    
    db.commit()
    return {"status": "success", "message": "Item added to cart"}, 200

@cart_bp.route('remove/', methods=['POST'])
def remove_from_cart():
    """Remove a single product from the cart by its ProductID."""
    if 'session_id' not in session:
        return redirect(url_for('cart.view_cart'))

    cart_id = session['session_id']
    product_id = request.form['product_id']

    db = get_db()
    db.execute("""
        DELETE FROM Shopping_cart 
        WHERE ProductID = ? AND ShopperID = ?
    """, (product_id, cart_id))
    db.commit()

    return redirect(url_for('cart.view_cart'))

@cart_bp.route('checkout/', methods=['GET', 'POST'])
def checkout():
    """Checkout the cart."""
    if request.method == 'POST':
        # Ensure the user is logged in by checking both user_id and session_id.
        if 'user_id' not in session or 'session_id' not in session:
            return redirect(url_for('user.login'))

        cart_id = session.get('session_id')
        if not cart_id:
            print("No cart found, redirect to cart view")
            return redirect(url_for('cart.view_cart'))

        db = get_db()

            # 检查购物车是否为空
        cart_items = db.execute("""
            SELECT COUNT(*) as count FROM Shopping_cart WHERE ShopperID = ?
        """, (cart_id,)).fetchone()

        if cart_items['count'] == 0:
            flash("Your shopping cart is empty. Please add items before checkout.", "danger")
            return redirect(url_for('cart.view_cart'))  # 购物车为空，返回购物车页面

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

            try:
                # Clear all cart items for this session_id.
                db.execute("DELETE FROM Shopping_Cart WHERE ShopperID = ?", (cart_id,))
                db.commit()

                # Remove stale cart entries (older than 1 month)
                db.execute("DELETE FROM Shopping_Cart WHERE AddedAt < datetime('now', '-1 month')")
                db.commit()

                flash("Order placed successfully, thank you!")
                return redirect(url_for('orders.view_orders'))
            except Exception as e:
                db.rollback()
                flash(f"An error occurred during checkout: {e}")
                return redirect(url_for('cart.view_cart'))
        else:
            return redirect(url_for('cart.view_cart'))

    return render_template('cart/checkout.html')
