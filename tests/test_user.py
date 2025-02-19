import pytest
from flask import g, session
from flaskr.db import get_db

def test_register(client, app):
    assert client.get('/user/register').status_code == 200
    response = client.post(
        '/user/register', data={'username': 'ABCDE', 'password': 'password'}
    )
    assert response.headers["Location"] == "/user/login"

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM Customers WHERE CustomerID = 'ABCDE'",
        ).fetchone() is not None

@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', b'User ID is required.'),
    ('ABCD', '', b'User ID must be exactly 5 characters.'),
    ('ABCDE', '', b'Password is required.'),
))
def test_register_validate_input(client, username, password, message):
    response = client.post(
        '/user/register',
        data={'username': username, 'password': password}
    )
    assert message in response.data

def test_login(client, auth):
    assert client.get('/user/login').status_code == 200
    response = auth.login()
    assert response.headers["Location"] == "/"

    with client:
        client.get('/')
        assert session['user_id'] == 'ABCDE'
        assert g.user['UserID'] == 'ABCDE'

@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('ABCDE', 'wrongpassword', b'Password incorrect, please try again.'),
    ('wronguser', 'password', b'Username not found, please make sure username is correct or register.'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data

def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session
