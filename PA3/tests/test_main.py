# tests/test_main.py

import os
import sys
import pytest
from flask import Flask

# Ensure project root is on the import path
sys.path.insert(0, os.getcwd())

# Import your blueprints
import flaskr.views.main as main_module
import flaskr.views.bill as bill_module
import flaskr.views.unit as unit_module

main_bp = main_module.main_bp
bill_bp = bill_module.bill_bp
unit_bp = unit_module.unit_bp

@pytest.fixture
def app():
    # Point Flask at the real templates folder so render_template() finds your HTML
    templates_path = os.path.join(os.getcwd(), 'flaskr', 'templates')
    app = Flask(__name__, template_folder=templates_path)

    # Register all blueprints referenced in dashboard.html
    app.register_blueprint(main_bp)
    app.register_blueprint(bill_bp)
    app.register_blueprint(unit_bp)

    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_index_route(client):
    resp = client.get('/')
    assert resp.status_code == 200
    # The rendered index.html should include an <html> tag
    assert b'<html' in resp.data.lower()

def test_dashboard_route(client):
    resp = client.get('/dashboard')
    assert resp.status_code == 200
    # The rendered dashboard.html should include an <html> tag
    assert b'<html' in resp.data.lower()
