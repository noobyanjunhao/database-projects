from flask import Blueprint, request, session, redirect, url_for, render_template, flash
from flaskr.db import get_db
from datetime import datetime, timedelta

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')

def get_est_time():
    """Get the current time in EST without using pytz."""
    utc_time = datetime.utcnow()
    # Adjust for EST (UTC-5)
    est_time = utc_time - timedelta(hours=5)
    return est_time

@cart_bp.route('/')
def view_cart():
    """Show all items in this shopper's cart."""
    # Use the pre-created session_id (fallback to generating one if missing)
    
    cart_id = session['session_id']
    db = get_db()

    # Retrieve rows matching the session_id as the ShopperID, including product names.
    rows = db.execute("""
        SELECT sc.ProductID, sc.Quantity, sc.AddedAt, p.ProductName, p.UnitPrice
        FROM Shopping_cart sc
        JOIN Products p ON sc.ProductID = p.ProductID
        WHERE sc.ShopperID = ?
    """, (cart_id,)).fetchall()

    # Calculate total price for each item and create a new dictionary
    items = []
    for row in rows:
        item = dict(row)  # Convert sqlite3.Row to a dictionary
        item['total_price'] = item['UnitPrice'] * item['Quantity']
        items.append({
            'product_id': item['ProductID'],
            'quantity': item['Quantity'],
            'timestamp': item['AddedAt'],  
            'name': item['ProductName'],   
            'price': item['UnitPrice'],
            'total_price': item['total_price']
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
    existing_item = db.execute("""
        SELECT Quantity FROM Shopping_cart 
        WHERE ShopperID = ? AND ProductID = ?
    """, (cart_id, product_id)).fetchone()
    if existing_item:
        # Increase the quantity by the added amount
        new_quantity = existing_item['Quantity'] + added_quantity
        db.execute("""
            UPDATE Shopping_cart 
            SET Quantity = ?, AddedAt = ? 
            WHERE ShopperID = ? AND ProductID = ?
        """, (new_quantity, get_est_time(), cart_id, product_id))
    else:
        # Insert a new row for the product
        db.execute("""
            INSERT INTO Shopping_cart (ShopperID, ProductID, Quantity, AddedAt)
            VALUES (?, ?, ?, ?)
        """, (cart_id, product_id, added_quantity, get_est_time()))
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

@cart_bp.route('/update_quantity', methods=['POST'])
def update_quantity():
    product_id = request.form.get('product_id')
    quantity = request.form.get('quantity')
    # Ensure session_id is present
    if 'session_id' not in session:
        return redirect(url_for('cart.view_cart'))
    cart_id = session['session_id']
    db = get_db()
    db.execute("""
        UPDATE Shopping_cart 
        SET Quantity = ? 
        WHERE ShopperID = ? AND ProductID = ?
    """, (int(quantity), cart_id, product_id))
    db.commit()
    return redirect(url_for('cart.view_cart'))

