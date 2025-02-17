from flask import Blueprint, request, session, redirect, url_for, render_template, flash
from flask.db import get_db
import secrets

cart_bp = Blueprint('cart', __name__, url_prefix = '/cart')
@cart_bp.route('/')
def view_cart():
    """show all item in cart during the user's session"""
    if 'cart id' not in session:
        #if no cart id, create one 
        session['cart_id'] = secrets.token_hex(16)

    cart_id = session['cart_id']

    db = get_db()
    rows = db.execute("""SELECT ProductID, Quantity, AddedAt FROM shopping_cart WHERE ShopperID= ?""", (cart_id)).fetchall()
    items = [{'product_id': row['ProductID'], 'quantity': row['Quantity'], 'timestamp': row['AddedAt']} for row in rows]

    return render_template('cart/cart_html',items = items) #you may change template route here

@cart_bp.route('add/', methods = ['POST'])
def add_to_cart():
    """add item to cart or update quantity"""
    if 'cart_id' not in session:
        session['cart_id'] = secrets.token_hex(16)
    
    cart_id = session['cart_id']
    product_id = request.form['product_id']
    quantity = int(request.form.get('quantity', 1)) #This set quantity to 1 if not provided  
    
    db = get_db()
    db.execute("""INSERT OR REPLACE INTO shopping_cart (ShopperID, ProductID, Quantity, AddedAt) 
                VALUES (
                :ShopperID, 
                :ProductID, 
                COALESCE((SELECT Quantity FROM shopping_cart WHERE ShopperID = :ShopperID AND ProductID = :ProductID), 0) + :Quantity, 
                CURRENT_TIMESTAMP
                )""", 
                {'ShopperID': cart_id, 'ProductID': product_id, 'Quantity': quantity})
    db.commit()

    return redirect(url_for('cart.view_cart'))

@cart_bp.route('remove/', methods = ['POST'])
def remove_from_cart():
    """remove item from cart"""
    if 'cart_id' not in session:
        #if no cart, no need to remove item
        return redirect(url_for('cart.view_cart'))
    cart_id = session['cart_id']
    product_id = request.form['product_id']
    db = get_db()
    db.execute("""DELETE FROM shopping_cart 
                WHERE ShopperID = ? AND ProductID = ?""", (cart_id, product_id))
    db.commit()
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('checkout/', methods=['GET', 'POST'])
def checkout():
    """checkout the cart"""
    if request.method == 'POST':
        # Ensure the user is logged in by checking the session
        if 'user_id' not in session or 'session_id' not in session:
            # User is not logged in, redirect to login
            return redirect(url_for('user.login'))

        cart_id = session.get('cart_id')
        if not cart_id:
            # No cart found, redirect to cart view
            return redirect(url_for('cart.view_cart'))

        db = get_db()
        error = None

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
            try:
                # Transfer items from Shopping_Cart to Orders
                db.execute("""
                    INSERT INTO Orders (UserID, ProductID, Quantity, OrderDate)
                    SELECT ?, ProductID, Quantity, CURRENT_TIMESTAMP
                    FROM Shopping_Cart
                    WHERE ShopperID = ?
                """, (user_id, cart_id))

                # Delete items from Shopping_Cart that are now in Orders
                db.execute("DELETE FROM Shopping_Cart WHERE ShopperID = ?", (cart_id,))

                # Clean up old cart entries (older than a month)
                db.execute("DELETE FROM Shopping_Cart WHERE AddedAt < datetime('now', '-1 month')")

                db.commit()
            except Exception as e:
                db.rollback()
                error = "An error occurred during checkout. Please try again."
                flash(error)
                return redirect(url_for('cart.view_cart'))

            # Redirect to orders page after checkout
            return redirect(url_for('orders.view_orders'))
        else:
            # User decided not to place an order, redirect back to cart
            return redirect(url_for('cart.view_cart'))

    return render_template('cart/checkout.html')
