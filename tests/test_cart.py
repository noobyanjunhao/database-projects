# tests/test_cart.py
import pytest
from flaskr.db import get_db
from datetime import datetime, timedelta
from flaskr.cart import get_est_time

def test_view_cart_empty(client):
    """
    If the cart is empty, the template should show no items.
    By default, session['session_id'] might not be set.
    We can set it manually in the test client, or rely on some code to create it.
    """
    with client.session_transaction() as sess:
        sess['session_id'] = 'test-session-123'  # manually set the session
    
    response = client.get('/cart/')
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    # Depending on your template, you might look for "No items" or check that no rows appear.
    # Adjust to match the actual template output.
    assert "ProductName" not in html
    assert "Quantity" not in html

def test_add_to_cart(client):
    """
    POST to /cart/add/ with a product_id and quantity.
    Then verify that the cart has that item.
    """
    with client.session_transaction() as sess:
        sess['session_id'] = 'test-session-123'
    
    # Add item
    response = client.post('/cart/add/', data={
        'product_id': '42',
        'quantity': '2'
    })

    print("Response JSON from /cart/add/:", response.json)

    # The route returns JSON {"status": "success", "message": "..."}
    assert response.status_code == 200
    assert response.json.get('status') == 'success'

    # Now view the cart
    response = client.get('/cart/')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    print("Cart HTML output:", html)
    # Check that we see the product ID or name in the cart
    assert "42" in html or "ProductName" in html

    # Optionally check DB directly
    with client.application.app_context():
        db = get_db() 
        row = db.execute("""
            SELECT * FROM Shopping_cart
            WHERE ShopperID = ? AND ProductID = ?
        """, ('test-session-123', '42')).fetchone()
        assert row is not None
        assert row['Quantity'] == 2

def test_remove_from_cart(client):
    """
    First add an item, then remove it.
    Finally, confirm it no longer appears in the cart or DB.
    """
    with client.session_transaction() as sess:
        sess['session_id'] = 'test-session-123'

    # Add item
    client.post('/cart/add/', data={'product_id': '42', 'quantity': '2'})
    
    # Remove item
    response = client.post('/cart/remove/', data={'product_id': '42'})
    # The route issues a redirect to /cart/
    assert response.status_code in (302, 303)

    # Check cart page
    response = client.get('/cart/')
    html = response.get_data(as_text=True)
    # Ensure "42" is gone
    assert "42" not in html

    # Optionally check DB
    with client.application.app_context():
        db = get_db()
        row = db.execute("""
            SELECT * FROM Shopping_cart
            WHERE ShopperID = ? AND ProductID = ?
        """, ('test-session-123', '42')).fetchone()
        assert row is None

def test_cleanup_old_cart_entries(app):
    """
    Directly test the cleanup_old_cart_entries function by inserting
    an old row and verifying that it gets removed.
    """
    from flaskr.cart import cleanup_old_cart_entries
    
    with app.app_context():
        db = get_db()
        shopper_id = 'test-session-old'
        old_time = get_est_time() - timedelta(days=60)  # older than 30 days

        # Insert an old entry
        db.execute("""
            INSERT INTO Shopping_cart (ShopperID, ProductID, Quantity, AddedAt)
            VALUES (?, ?, ?, ?)
        """, (shopper_id, 99, 5, old_time))
        db.commit()

        # Call the cleanup function
        cleanup_old_cart_entries()

        # Check the row is removed
        row = db.execute("""
            SELECT * FROM Shopping_cart
            WHERE ShopperID = ? AND ProductID = ?
        """, (shopper_id, 99)).fetchone()
        assert row is None
