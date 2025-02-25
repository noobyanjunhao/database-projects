from flaskr import create_app
from flask import Flask
from flask.testing import FlaskClient

def test_config(app: Flask) -> None:
    assert not create_app().testing
    assert app.testing

def test_hello(client: FlaskClient) -> None:
    response = client.get('/hello')
    assert response.data == b'Hello, World!' 
