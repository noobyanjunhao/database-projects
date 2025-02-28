import pytest
from flaskr.db import get_db
from typing import Any, Callable

@pytest.fixture
def auth(client: Any) -> Any:
    class AuthActions:
        def login(self, username: str, password: str) -> Any:
            return client.post('/user/login', data={'username': username, 'password': password})

        def logout(self) -> Any:
            return client.get('/user/logout')

    return AuthActions()

def test_checkout_requires_login(client: Any, auth: Any, app: Any) -> None:
    """Ensure users must be logged in to access checkout."""
    response = client.get('/checkout/')
    assert response.status_code == 302
    assert response.headers['Location'] == '/user/login'

    client.post('/user/register', data={'username': 'NEWUS', 'password': 'newpassword'})
    response = auth.login('NEWUS', 'newpassword')
    assert response.status_code == 302
    assert response.headers['Location'] == '/products'


def test_checkout_empty_cart(client: Any, auth: Any) -> None:
    """Ensure users cannot checkout with an empty cart."""
    client.post('/user/register', data={'username': 'NEWUS', 'password': 'newpassword'})
    auth.login('NEWUS', 'newpassword')
    response = client.get('/checkout/')
    assert response.status_code == 302
    assert response.headers['Location'] == '/cart/'


def test_checkout_invalid_session(client: Any, auth: Any) -> None:
    """Ensure users with invalid sessions are redirected to login."""
    auth.login('NEWUS', 'newpassword')
    # Manually override session_id to an invalid value
    with client.session_transaction() as sess:
        sess['session_id'] = 'fake-session-xyz'
    response = client.get('/checkout/')
    assert response.status_code == 302
    assert response.headers['Location'] == '/user/login'


def test_checkout_database_error(client: Any, auth: Any, app: Any) -> None:
    """Ensure database errors during checkout are handled correctly."""
    client.post('/user/register', data={'username': 'NEWUS', 'password': 'newpassword'})
    auth.login('NEWUS', 'newpassword')
    client.post('/cart/add/', data={'product_id': '42', 'quantity': '2'})

    with app.app_context():
        db = get_db()
        db.execute("DROP TABLE Orders")  # Induce a DB error
        db.commit()

    response = client.post('/checkout/', data={
        'ship_name': 'John Doe',
        'ship_address': '123 Main St',
        'ship_city': 'Anytown',
        'ship_country': 'USA',
        'place_order': 'true'
    })

    assert response.status_code == 302
    assert response.headers['Location'] == '/cart/'


def test_checkout_get_request(client: Any, auth: Any) -> None:
    """Ensure GET requests to checkout page return the correct template."""
    client.post('/user/register', data={'username': 'NEWUS', 'password': 'newpassword'})
    auth.login('NEWUS', 'newpassword')

    client.post('/cart/add/', data={'product_id': '1', 'quantity': '1'})
    
    response = client.get('/checkout/')
    assert response.status_code == 200
    assert b"Checkout" in response.data


def test_successful_checkout_clears_cart(client: Any, auth: Any, app: Any) -> None:
    """Ensure successful checkout clears the cart."""
    client.post('/user/register', data={'username': 'NEWUS', 'password': 'newpassword'})
    auth.login('NEWUS', 'newpassword')

    client.post('/cart/add/', data={'product_id': '1', 'quantity': '1'})

    # Perform the checkout
    response = client.post('/checkout/', data={
        'ship_name': 'John Doe',
        'ship_address': '123 Main St',
        'ship_city': 'Anytown',
        'ship_country': 'USA',
        'place_order': 'true'
    })
    assert response.status_code == 302
    assert response.headers['Location'] == '/orders/'

    # Get the session_id outside of app_context
    with client.session_transaction() as sess:
        session_id = sess['session_id']

    # Now check if the cart is empty
    with app.app_context():
        db = get_db()
        cart_count = db.execute(
            "SELECT COUNT(*) FROM Shopping_cart WHERE ShopperID = ?", 
            (session_id,)
        ).fetchone()[0]
        assert cart_count == 0


def test_order_is_correctly_stored(client: Any, auth: Any, app: Any) -> None:
    """Ensure order details are correctly stored in the database."""
    client.post('/user/register', data={'username': 'NEWUS', 'password': 'newpassword'})
    auth.login('NEWUS', 'newpassword')

    client.post('/cart/add/', data={'product_id': '1', 'quantity': '1'})

    response = client.post('/checkout/', data={
        'ship_name': 'John Doe',
        'ship_address': '123 Main St',
        'ship_city': 'Anytown',
        'ship_country': 'USA',
        'place_order': 'true'
    })
    assert response.status_code == 302
    assert response.headers['Location'] == '/orders/'

    with app.app_context():
        db = get_db()
        # Check the newly inserted order
        order = db.execute(
            "SELECT * FROM Orders WHERE CustomerID = ?", 
            ("NEWUS",)
        ).fetchone()
        assert order is not None
        assert order["ShipName"] == "John Doe"
        assert order["ShipAddress"] == "123 Main St"
        assert order["ShipCity"] == "Anytown"
        assert order["ShipCountry"] == "USA"


def test_checkout_with_different_shipping_options(client: Any, auth: Any, app: Any) -> None:
    """Ensure different shipping options are correctly stored."""
    client.post('/user/register', data={'username': 'NEWUS', 'password': 'newpassword'})
    auth.login('NEWUS', 'newpassword')

    client.post('/cart/add/', data={'product_id': '1', 'quantity': '1'})

    response = client.post('/checkout/', data={
        'ship_name': 'Alice Smith',
        'ship_address': '456 Elm St',
        'ship_city': 'Smalltown',
        'ship_region': 'CA',
        'ship_postal_code': '12345',
        'ship_country': 'USA',
        'ship_via': '2',
        'place_order': 'true'
    })
    assert response.status_code == 302
    assert response.headers['Location'] == '/orders/'

    with app.app_context():
        db = get_db()
        order = db.execute(
            "SELECT * FROM Orders WHERE CustomerID = ?", 
            ("NEWUS",)
        ).fetchone()
        assert order is not None
        assert order["ShipName"] == "Alice Smith"
        assert order["ShipAddress"] == "456 Elm St"
        assert order["ShipCity"] == "Smalltown"
        assert order["ShipRegion"] == "CA"
        assert order["ShipPostalCode"] == "12345"
        assert order["ShipCountry"] == "USA"
        assert order["ShipVia"] == 2


def test_multiple_users_checkout_separately(client: Any, auth: Any, app: Any) -> None:
    """Ensure multiple users can checkout independently without conflicts."""
    client.post('/user/register', data={'username': 'USER1', 'password': 'pass1'})
    auth.login('USER1', 'pass1')
    client.post('/cart/add/', data={'product_id': '1', 'quantity': '2'})

    # Switch user
    client.post('/user/register', data={'username': 'USER2', 'password': 'pass2'})
    auth.login('USER2', 'pass2')
    client.post('/cart/add/', data={'product_id': '2', 'quantity': '1'})

    response1 = client.post('/checkout/', data={
        'ship_name': 'User One',
        'ship_address': '111 First St',
        'ship_city': 'CityA',
        'ship_country': 'USA',
        'place_order': 'true'
    })

    response2 = client.post('/checkout/', data={
        'ship_name': 'User Two',
        'ship_address': '222 Second St',
        'ship_city': 'CityB',
        'ship_country': 'Canada',
        'place_order': 'true'
    })

    assert response1.status_code == 302
    assert response2.status_code == 302
