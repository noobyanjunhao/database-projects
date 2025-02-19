from flask import Blueprint, request, session, redirect, url_for, render_template, flash
from flaskr.db import get_db

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')

@cart_bp.route('/')
def view_cart():
    """Show all items in this shopper's cart."""
    # Use the pre-created session_id (fallback to generating one if missing)
    
    cart_id = session['session_id']
    db = get_db()

    # Retrieve rows matching the session_id as the ShopperID, including product names.
    rows = db.execute("""
        SELECT p.ProductName, sc.Quantity, sc.AddedAt 
        FROM Shopping_cart sc
        JOIN Products p ON sc.ProductID = p.ProductID
        WHERE sc.ShopperID = ?
    """, (cart_id,)).fetchall()

    items = []
    for row in rows:
        items.append({
            'product_name': row['ProductName'],
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

