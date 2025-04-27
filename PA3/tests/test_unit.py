# tests/test_unit.py

import os
import sys
import json
import datetime
import pytest
from flask import Flask

# Ensure project root is on the import path
sys.path.insert(0, os.getcwd())

# Import all needed blueprints
import flaskr.views.main as main_module
import flaskr.views.bill as bill_module
import flaskr.views.export as export_module
import flaskr.views.unit as unit_module

main_bp   = main_module.main_bp
bill_bp   = bill_module.bill_bp
export_bp = export_module.export_bp
unit_bp   = unit_module.unit_bp

class DummyCursor:
    def __init__(self, rows):
        self._rows = rows

    def fetchall(self):
        return self._rows

    def fetchone(self):
        return self._rows[0] if self._rows else None

class SeqDB:
    """Returns successive row‐sets on each execute() call."""
    def __init__(self, sequences):
        self._seq = sequences[:]
        self.committed = False

    def execute(self, query, args=None):
        rows = self._seq.pop(0)
        return DummyCursor(rows)

    def commit(self):
        self.committed = True

@pytest.fixture
def app():
    # Point Flask to your actual templates directory
    templates_path = os.path.join(os.getcwd(), 'flaskr', 'templates')
    app = Flask(__name__, template_folder=templates_path)

    # Register all blueprints that your templates reference
    app.register_blueprint(main_bp)
    app.register_blueprint(unit_bp)
    app.register_blueprint(bill_bp)
    app.register_blueprint(export_bp)

    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_units_overview(monkeypatch, client):
    # One sample row for /units
    rows = [{
        "apartment_id": 1,
        "unit_number": "101",
        "unit_size": "500 sqft",
        "ownership_type": "rented",
        "is_special": 1,
        "has_lease": 1,
        "tenant_name": "Alice",
        "monthly_rent": 1200,
        "end_date": datetime.date(2025, 12, 31),
    }]
    dummy_db = SeqDB([rows])
    monkeypatch.setattr(unit_module, 'get_db', lambda: dummy_db)

    resp = client.get('/units')
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "101" in html
    assert "Alice" in html

def test_unit_detail_not_found(monkeypatch, client):
    # No lease row => 404
    dummy_db = SeqDB([[]])
    monkeypatch.setattr(unit_module, 'get_db', lambda: dummy_db)

    resp = client.get('/unit/42')
    assert resp.status_code == 404

def test_unit_detail_success(monkeypatch, client):
    # Prepare the 7 sequential DB calls:
    # 1) lease_info
    lease_info = [{
        "apartment_id": 1,
        "unit_number": "101",
        "unit_size": "500 sqft",
        "ownership_type": "rented",
        "is_special": 1,
        "full_name": "Alice",
        "email": "alice@example.com",
        "monthly_rent": 1200.0,
        "start_date": datetime.datetime(2025, 1, 1),
        "end_date": datetime.datetime(2025, 12, 31),
        "lease_id": 10
    }]
    # 2) bills (id, sent_at, total_amount)
    bills = [{
        "id": 1,
        "sent_at": datetime.datetime(2025, 4,  1),
        "total_amount": 1250
    }]
    # 3) all_bills (same shape as bills)
    all_bills = bills[:]
    # 4) bill_options (id, billing_month as datetime, rent_amount, total_amount)
    bill_options = [{
        "id": 1,
        "billing_month": datetime.datetime(2025, 4, 1),
        "rent_amount": 1200,
        "total_amount": 1250
    }]
    # 5) payments (id, payment_date, amount)
    payments = [{
        "id": 2,
        "payment_date": datetime.datetime(2025, 4, 5),
        "amount": 1250
    }]
    # 6) all_payments (same shape)
    all_payments = payments[:]
    # 7) all_bills_calc for computing balance
    all_bills_calc = [{
        "rent_amount": 1200,
        "other_charges": json.dumps({"gas": 50})
    }]

    seq = [lease_info, bills, all_bills, bill_options, payments, all_payments, all_bills_calc]
    dummy_db = SeqDB(seq)
    monkeypatch.setattr(unit_module, 'get_db', lambda: dummy_db)

    resp = client.get('/unit/1')
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    # Verify key pieces rendered
    assert "101" in html
    assert "Alice" in html
    # And the billing_month formatting should appear as "2025-04"
    assert "2025-04" in html

def test_update_lease_not_found(monkeypatch, client):
    # No lease => 404
    dummy_db = SeqDB([[]])
    monkeypatch.setattr(unit_module, 'get_db', lambda: dummy_db)

    resp = client.post('/unit/99/update-lease', json={
        "tenant_name": "Bob",
        "tenant_email": "bob@example.com",
        "start_date": "2025-02-01",
        "end_date": "2025-12-31",
        "monthly_rent": 1000,
        "ownership_type": "rented",
        "is_special": 0
    })
    assert resp.status_code == 404

def test_update_lease_success(monkeypatch, client):
    # First call returns lease row; next three are update queries
    lease_row = [{"lease_id": 10, "tenant_id": 20}]
    dummy_db = SeqDB([lease_row, [], [], []])
    monkeypatch.setattr(unit_module, 'get_db', lambda: dummy_db)

    payload = {
        "tenant_name": "Bob",
        "tenant_email": "bob@example.com",
        "start_date": "2025-02-01",
        "end_date": "2025-12-31",
        "monthly_rent": 1000,
        "ownership_type": "rented",
        "is_special": 0
    }
    resp = client.post('/unit/1/update-lease', json=payload)
    assert resp.status_code == 200
    assert dummy_db.committed
