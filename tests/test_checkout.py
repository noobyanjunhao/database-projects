import pytest
from flaskr.db import get_db

@pytest.fixture
def auth(client):
    class AuthActions:
        def login(self, username, password):
            return client.post('/auth/login', data={'username': username, 'password': password})

        def logout(self):
            return client.get('/auth/logout')

    return AuthActions()

def test_checkout_requires_login(client, auth, app):
    # Attempt to access checkout without logging in
    response = client.get('/checkout/')
    assert response.status_code == 302  # Expect redirect
    assert response.headers['Location'] == '/user/login'  # Expect redirect to login

    # Log in the user
    response = auth.login('testuser', 'hashedpassword123')
    assert response.status_code == 200  # Ensure login was successful

    # Add an item to the cart
    with client.session_transaction() as sess:
        sess['session_id'] = 'test-session-123'
        sess['user_id'] = 'testuser'  # Ensure the session is associated with the logged-in user

    # Debugging: Check session state
    with client.session_transaction() as sess:
        print(f"Session after login: {sess}")

    client.post('/cart/add/', data={'product_id': '42', 'quantity': '2'})

    # Test checkout page loads after login
    response = client.get('/checkout/')
    assert response.status_code == 200

    # Test successful checkout
    response = client.post('/checkout/', data={
        'ship_name': 'John Doe',
        'ship_address': '123 Main St',
        'ship_city': 'Anytown',
        'ship_country': 'USA',
        'place_order': 'true'
    })
    assert response.headers['Location'] == '/orders'

    # Check the database for the new order
    with app.app_context():
        db = get_db()
        order = db.execute("SELECT * FROM Orders WHERE CustomerID = 'testuser'").fetchone()
        assert order is not None
