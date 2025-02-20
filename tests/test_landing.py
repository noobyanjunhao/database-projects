from jinja2 import TemplateNotFound
import pytest

def test_landing_page(client):
    response = client.get('/')
    assert response.status_code == 200
    # If your landing page has "Welcome" text:
    assert b"Welcome" in response.data

def test_missing_template(client, monkeypatch):
    # Simulate a missing template scenario
    def mock_render_template(*args, **kwargs):
        raise TemplateNotFound("landing.html")
    
    monkeypatch.setattr('flaskr.landing.render_template', mock_render_template)
    
    with pytest.raises(TemplateNotFound):
        client.get('/') 