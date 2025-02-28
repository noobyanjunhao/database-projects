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
    response = client.get('/checkout/')
    assert response.status_code == 302
    assert response.headers['Location'] == '/user/login'

    client.post('/user/register', data={'username': 'NEWUS', 'password': 'newpassword'})
    response = auth.login('NEWUS', 'newpassword')
    assert response.status_code == 302
    assert response.headers['Location'] == '/products'

def test_checkout_empty_cart(client: Any, auth: Any) -> None:
    client.post('/user/register', data={'username': 'NEWUS', 'password': 'newpassword'})
    auth.login('NEWUS', 'newpassword')
    response = client.get('/checkout/')
    assert response.status_code == 302
    assert response.headers['Location'] == '/cart/'

def test_checkout_invalid_session(client: Any, auth: Any) -> None:
    auth.login('NEWUS', 'newpassword')
    with client.session_transaction() as sess:
        sess['session_id'] = 'fake-session-xyz'
    response = client.get('/checkout/')
    assert response.status_code == 302
    assert response.headers['Location'] == '/user/login'

def test_checkout_database_error(client: Any, auth: Any, app: Any) -> None:
    client.post('/user/register', data={'username': 'NEWUS', 'password': 'newpassword'})
    auth.login('NEWUS', 'newpassword')
    client.post('/cart/add/', data={'product_id': '42', 'quantity': '2'})

    with app.app_context():
        db = get_db()
        db.execute("DROP TABLE Orders")
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
    client.post('/user/register', data={'username': 'NEWUS', 'password': 'newpassword'})
    auth.login('NEWUS', 'newpassword')

    client.post('/cart/add/', data={'product_id': '1', 'quantity': '1'})
    
    response = client.get('/checkout/')
    assert response.status_code == 200
    assert b"Checkout" in response.data

