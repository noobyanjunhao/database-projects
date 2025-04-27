# tests/test_bills.py

import os
import sys
import json
import datetime
import pytest
from flask import Flask

# Ensure project root is on the import path so we can import flaskr
sys.path.insert(0, os.getcwd())

# Import your blueprints
import flaskr.views.main as main_module
import flaskr.views.unit as unit_module
import flaskr.views.bill as bill_module

main_bp = main_module.main_bp
unit_bp = unit_module.unit_bp
bill_bp = bill_module.bill_bp

class DummyCursor:
    def __init__(self, rows):
        self._rows = rows

    def fetchall(self):
        return self._rows

    def fetchone(self):
        return self._rows[0] if self._rows else None

class DummyDB:
    def __init__(self, rows=None, fail=False):
        self.rows = rows or []
        self.committed = False
        self.fail = fail

    def execute(self, query, args=None):
        if self.fail:
            raise Exception("DB error")
        return DummyCursor(self.rows)

    def commit(self):
        self.committed = True

@pytest.fixture
def app():
    # Point Flask at the correct templates folder
    templates_path = os.path.join(os.getcwd(), 'flaskr', 'templates')
    app = Flask(__name__, template_folder=templates_path)

    # Register all blueprints needed for url_for
    app.register_blueprint(main_bp)
    app.register_blueprint(unit_bp)
    app.register_blueprint(bill_bp)

    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_bill_payment_dashboard_filters(monkeypatch, client):
    rows = [
        {'apartment_id': 1, 'unit_number': '101', 'ownership_type': 'rented', 'is_special': 0, 'full_name': 'Alice'},
        {'apartment_id': 2, 'unit_number': '102', 'ownership_type': 'sold',   'is_special': 0, 'full_name': 'Bob'},
        {'apartment_id': 3, 'unit_number': '103', 'ownership_type': 'rented', 'is_special': 1, 'full_name': None},
    ]
    dummy_db = DummyDB(rows=rows)
    monkeypatch.setattr(bill_module, 'get_db', lambda: dummy_db)

    resp = client.get('/bill-payment')
    assert resp.status_code == 200
    text = resp.get_data(as_text=True)
    # Only the first (valid) row should appear
    assert '101' in text and 'Alice' in text
    assert '102' not in text
    assert '103' not in text

def test_create_bill_not_found(monkeypatch, client):
    dummy_db = DummyDB(rows=[])
    monkeypatch.setattr(bill_module, 'get_db', lambda: dummy_db)

    resp = client.post('/unit/5/create-bill', json={
        "billing_month": "2025-04",
        "rent_amount": 1000,
        "other_charges": {},
        "balance_used": 0,
        "total_amount": 1000
    })
    assert resp.status_code == 404

def test_create_bill_success(monkeypatch, client):
    lease_row = {'lease_id': 10, 'email': 'test@example.com', 'full_name': 'Test User'}
    dummy_db = DummyDB(rows=[lease_row])
    monkeypatch.setattr(bill_module, 'get_db', lambda: dummy_db)

    resp = client.post('/unit/1/create-bill', json={
        "billing_month": "2025-04",
        "rent_amount": 1200.50,
        "other_charges": {"water": 30},
        "balance_used": 100,
        "total_amount": 1130.50
    })
    assert resp.status_code == 200
    assert dummy_db.committed

def test_bill_detail_not_found(monkeypatch, client):
    dummy_db = DummyDB(rows=[])
    monkeypatch.setattr(bill_module, 'get_db', lambda: dummy_db)

    resp = client.get('/bill/999')
    assert resp.status_code == 404

def test_bill_detail_success(monkeypatch, client):
    # Use a datetime object so .strftime works in template
    bill_row = {
        "sent_at": datetime.datetime(2025, 4, 10),
        "billing_month": "2025-04",
        "rent_amount": 1200,
        "other_charges": json.dumps({"gas": 50}),
        "balance_used": 0,
        "total_amount": 1250,
        "full_name": "Alice",
        "unit_number": "201",
        "apartment_id": 1
    }
    dummy_db = DummyDB(rows=[bill_row])
    monkeypatch.setattr(bill_module, 'get_db', lambda: dummy_db)

    resp = client.get('/bill/1')
    assert resp.status_code == 200
    text = resp.get_data(as_text=True)
    assert '201' in text and 'Alice' in text

def test_create_payment_missing_fields(monkeypatch, client):
    dummy_db = DummyDB()
    monkeypatch.setattr(bill_module, 'get_db', lambda: dummy_db)

    resp = client.post('/unit/1/create-payment', json={})
    assert resp.status_code == 400

def test_create_payment_db_error(monkeypatch, client):
    dummy_db = DummyDB(fail=True)
    monkeypatch.setattr(bill_module, 'get_db', lambda: dummy_db)

    resp = client.post('/unit/1/create-payment', json={
        'bill_id': 1,
        'amount': 100,
        'payment_date': '2025-04-15',
        'check_number': 'A123',
        'remitter_name': 'Alice'
    })
    assert resp.status_code == 500

def test_create_payment_success(monkeypatch, client):
    dummy_db = DummyDB()
    monkeypatch.setattr(bill_module, 'get_db', lambda: dummy_db)

    resp = client.post('/unit/1/create-payment', json={
        'bill_id': 2,
        'amount': 200,
        'payment_date': '2025-04-20',
        'check_number': 'B456',
        'remitter_name': 'Bob'
    })
    assert resp.status_code == 200
    assert dummy_db.committed

def test_payment_detail_not_found(monkeypatch, client):
    dummy_db = DummyDB(rows=[])
    monkeypatch.setattr(bill_module, 'get_db', lambda: dummy_db)

    resp = client.get('/payment/123')
    assert resp.status_code == 404

def test_payment_detail_success(monkeypatch, client):
    payment_row = {
        "id": 5,
        "bill_id": 2,
        "amount": 200,
        # datetime for compatibility with .strftime
        "payment_date": datetime.datetime(2025, 4, 20),
        "check_number": "C789",
        "remitter_name": "Carol",
        "unit_number": "301",
        "apartment_id": 3,
        "full_name": "Carol"
    }
    dummy_db = DummyDB(rows=[payment_row])
    monkeypatch.setattr(bill_module, 'get_db', lambda: dummy_db)

    resp = client.get('/payment/5')
    assert resp.status_code == 200
    text = resp.get_data(as_text=True)
    assert '301' in text and 'Carol' in text
