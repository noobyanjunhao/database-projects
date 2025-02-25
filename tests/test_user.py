import pytest
from flask import g, session
from flaskr.db import get_db
from werkzeug.security import check_password_hash

class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username, password):
        return self._client.post('/user/login', data={'username': username, 'password': password})

    def logout(self):
        return self._client.get('/user/logout')

@pytest.fixture
def auth(client):
    return AuthActions(client)

def test_register(client, app):
    response = client.get('/user/register')
    assert response.status_code == 200

    # 注册成功
    response = client.post('/user/register', data={'username': 'NEWUS', 'password': 'newpassword'})
    assert response.status_code == 302
    assert response.headers['Location'] == '/user/login'

    # 验证数据库
    with app.app_context():
        db = get_db()
        user = db.execute("SELECT * FROM Authentication WHERE UserID = 'NEWUS'").fetchone()
        assert user is not None
        assert check_password_hash(user['PasswordHash'], 'newpassword')

def test_register_failures(client):
    """测试注册失败的情况"""
    # 用户 ID 太短
    response = client.post('/user/register', data={'username': 'AB', 'password': 'newpassword'})
    assert b"User ID must be exactly 5 characters." in response.data

    # 用户 ID 为空
    response = client.post('/user/register', data={'username': '', 'password': 'newpassword'})
    assert b"User ID is required." in response.data

    # 密码为空
    response = client.post('/user/register', data={'username': 'ABCDE', 'password': ''})
    assert b"Password is required." in response.data

    # 用户已存在
    client.post('/user/register', data={'username': 'NEWUS', 'password': 'newpassword'})
    response = client.post('/user/register', data={'username': 'NEWUS', 'password': 'anotherpass'})
    assert b"User NEWUS is already registered." in response.data

def test_login(client, auth):
    client.post('/user/register', data={'username': 'NEWUS', 'password': 'newpassword'})

    response = client.get('/user/login')
    assert response.status_code == 200

    # 正确登录
    response = auth.login('NEWUS', 'newpassword')
    assert response.status_code == 302
    assert response.headers['Location'] == '/products'

    # 确保 session 被正确设置
    with client.session_transaction() as session:
        assert session['user_id'] == 'NEWUS'

def test_login_failures(client, auth):
    """测试登录失败的情况"""
    # 用户不存在
    response = auth.login('FAKEU', 'newpassword')
    assert b"Username not found" in response.data

    # 密码错误
    client.post('/user/register', data={'username': 'NEWUS', 'password': 'newpassword'})
    response = auth.login('NEWUS', 'wrongpassword')
    assert b"Password incorrect" in response.data

def test_logout(client, auth):
    auth.login('NEWUS', 'newpassword')

    response = client.get('/user/logout')
    assert response.headers['Location'] == '/products'

