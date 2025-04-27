def test_index_route(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'<html' in resp.data.lower()

def test_dashboard_route(client):
    resp = client.get('/dashboard')
    assert resp.status_code == 200
    assert b'<html' in resp.data.lower()
