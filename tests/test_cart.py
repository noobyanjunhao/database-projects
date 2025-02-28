# tests/test_cart.py
import pytest
from flask.testing import FlaskClient
from flask import Flask
from flaskr.db import get_db
from datetime import datetime, timedelta
from flaskr.cart import get_est_time, cleanup_old_cart_entries

def test_view_cart_empty(client: FlaskClient) -> None:
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

def test_add_to_cart(client: FlaskClient) -> None:
    """
    POST to /cart/add/ with a product_id and quantity.
    Then verify that the cart has that item.
    """
    with client.session_transaction() as sess:
        sess['session_id'] = 'test-session-123'
    
    # Add item using an existing product_id (e.g., "1")
    response = client.post('/cart/add/', data={
        'product_id': '1',
        'quantity': '2'
    })
    # The route returns JSON {"status": "success", "message": "..."}
    assert response.status_code == 200
    assert response.json is not None
    assert response.json.get('status') == 'success'
    
    # Now view the cart
    response = client.get('/cart/')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    # Check that we see the product details in the rendered page.
    # We check for "1" or "Wireless Mouse" in case the template renders either.
    assert "1" in html or "Wireless Mouse" in html

    # Optionally check DB directly for product "1"
    with client.application.app_context():
        db = get_db()
        row = db.execute("""
            SELECT * FROM Shopping_cart
            WHERE ShopperID = ? AND ProductID = ?
        """, ('test-session-123', '1')).fetchone()
        assert row is not None
        assert row['Quantity'] == 2

    # Add another product (product_id "42")
    with client.session_transaction() as sess:
        sess['session_id'] = 'test-session-123'
    
    response = client.post('/cart/add/', data={
        'product_id': '42',
        'quantity': '2'
    })
    assert response.status_code == 200
    assert response.json is not None
    assert response.json.get('status') == 'success'

    # Instead of asserting "42" is in the HTML, verify directly in the DB.
    with client.application.app_context():
        db = get_db() 
        row = db.execute("""
            SELECT * FROM Shopping_cart
            WHERE ShopperID = ? AND ProductID = ?
        """, ('test-session-123', '42')).fetchone()
        assert row is not None
        assert row['Quantity'] == 2

def test_add_to_cart_existing_item(client: FlaskClient) -> None:
    """
    Test adding the same product twice to cover the 'if existing_item' update path.
    """
    with client.session_transaction() as sess:
        sess['session_id'] = 'test-session-123'
    
    # Add item initially
    client.post('/cart/add/', data={'product_id': '10', 'quantity': '2'})
    # Add the same item again
    client.post('/cart/add/', data={'product_id': '10', 'quantity': '3'})

    # Check that quantity is now 5 in the database
    with client.application.app_context():
        db = get_db()
        row = db.execute("""
            SELECT * FROM Shopping_cart
            WHERE ShopperID = ? AND ProductID = ?
        """, ('test-session-123', '10')).fetchone()
        assert row is not None
        assert row['Quantity'] == 5

def test_add_to_cart_no_quantity(client: FlaskClient) -> None:
    """
    Test adding a product without providing 'quantity' to ensure the default of 1 is used.
    """
    with client.session_transaction() as sess:
        sess['session_id'] = 'test-session-123'
    
    # Add item with no quantity field
    response = client.post('/cart/add/', data={'product_id': '99'})
    assert response.status_code == 200
    assert response.json.get('status') == 'success'

    with client.application.app_context():
        db = get_db()
        row = db.execute("""
            SELECT * FROM Shopping_cart
            WHERE ShopperID = ? AND ProductID = ?
        """, ('test-session-123', '99')).fetchone()
        assert row is not None
        # Should default to 1
        assert row['Quantity'] == 1

def test_remove_from_cart(client: FlaskClient) -> None:
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
    # Ensure product details for "42" are no longer present.
    assert "42" not in html

    # Optionally check DB
    with client.application.app_context():
        db = get_db()
        row = db.execute("""
            SELECT * FROM Shopping_cart
            WHERE ShopperID = ? AND ProductID = ?
        """, ('test-session-123', '42')).fetchone()
        assert row is None

def test_remove_from_cart_no_session_id(client: FlaskClient) -> None:
    """
    Test removing an item when no session_id is set.
    This covers the 'if "session_id" not in session' branch in remove_from_cart.
    """
    # Do NOT set session_id here.
    response = client.post('/cart/remove/', data={'product_id': '999'})
    # Should redirect to /cart/
    assert response.status_code in (302, 303)
    assert '/cart/' in response.headers.get('Location', '')

def test_cleanup_old_cart_entries(app: Flask) -> None:
    """
    Directly test the cleanup_old_cart_entries function by inserting
    an old row and verifying that it gets removed.
    """
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

def test_remove_from_cart_without_session(app):
    from flaskr.cart import remove_from_cart
    from flask import session, url_for

    # Create a request context for the /cart/remove/ endpoint
    with app.test_request_context('/cart/remove/', method='POST', data={'product_id': '999'}):
        # Clear the session to simulate no 'session_id'
        session.clear()
        # Call the remove_from_cart view directly
        response = remove_from_cart()
        # Check that the response is a redirect to the cart view
        assert response.status_code in (302, 303)
        # Verify that the redirect location is correct
        assert url_for('cart.view_cart') in response.location
