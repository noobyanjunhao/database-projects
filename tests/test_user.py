import pytest
from flask import g, session
from flaskr.db import get_db
from werkzeug.security import check_password_hash

class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username, password):
        return self._client.post(
            '/user/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/user/logout')

@pytest.fixture
def auth(client):
    return AuthActions(client)

def test_register(client, app):
    # Test GET request to registration page
    response = client.get('/user/register')
    assert response.status_code == 200

    # Test successful registration
    response = client.post('/user/register', 
                         data={'username': 'NEWUS', 'password': 'newpassword'})
    assert response.status_code == 302  # Expect redirect
    assert response.headers['Location'] == '/user/login'

    # Verify the user was created in the database
    with app.app_context():
        db = get_db()
        user = db.execute("SELECT * FROM Authentication WHERE UserID = 'NEWUS'").fetchone()
        assert user is not None
        assert check_password_hash(user['PasswordHash'], 'newpassword')

def test_login(client, auth):
    # Register the user so that they exist for login
    client.post('/user/register', data={'username': 'NEWUS', 'password': 'newpassword'})

    # Test GET request to login page
    response = client.get('/user/login')
    assert response.status_code == 200

    # Test successful login
    response = auth.login('NEWUS', 'newpassword')
    assert response.status_code == 302  # Expect redirect
    assert response.headers['Location'] == '/products'

    # Test session is set correctly
    with client.session_transaction() as session:
        assert session['user_id'] == 'NEWUS'

def test_logout(client, auth):
    auth.login('testuser', 'hashedpassword123')

    # Test logout
    response = client.get('/user/logout')
    assert response.headers['Location'] == '/products'
