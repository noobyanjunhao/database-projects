from flaskr import create_app

def test_config(app):
    assert not create_app().testing
    assert app.testing

def test_hello(client):
    response = client.get('/hello')
    assert response.data == b'Hello, World!' 
