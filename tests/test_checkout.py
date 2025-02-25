import pytest
from flaskr.db import get_db

@pytest.fixture
def auth(client):
    class AuthActions:
        def login(self, username, password):
            return client.post('/user/login', data={'username': username, 'password': password})

        def logout(self):
            return client.get('/user/logout')

    return AuthActions()

def test_checkout_requires_login(client, auth, app):
    response = client.get('/checkout/')
    assert response.status_code == 302
    assert response.headers['Location'] == '/user/login'

    client.post('/user/register', data={'username': 'NEWUS', 'password': 'newpassword'})
    response = auth.login('NEWUS', 'newpassword')
    assert response.status_code == 302
    assert response.headers['Location'] == '/products'

def test_checkout_empty_cart(client, auth):
    auth.login('NEWUS', 'newpassword')
    response = client.get('/checkout/')
    assert response.status_code == 302
    assert response.headers['Location'] == '/cart/'

def test_checkout_invalid_session(client, auth):
    auth.login('NEWUS', 'newpassword')
    with client.session_transaction() as sess:
        sess['session_id'] = 'fake-session-xyz'
    response = client.get('/checkout/')
    assert response.status_code == 302
    assert response.headers['Location'] == '/user/login'

def test_checkout_database_error(client, auth, app):
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

def test_checkout_get_request(client, auth):
    auth.login('NEWUS', 'newpassword')
    response = client.get('/checkout/')
    assert response.status_code == 200
    assert b"Checkout" in response.data

