# tests/test_export.py

import os
import sys
import pytest
from flask import Flask

# Make sure we can import flaskr
sys.path.insert(0, os.getcwd())

import flaskr.views.export as export_module

class DummyCursor:
    def __init__(self, rows):
        self._rows = rows

    def fetchall(self):
        return self._rows

class DummyDB:
    def __init__(self, rows=None):
        self.rows = rows or []

    def execute(self, query):
        return DummyCursor(self.rows)

@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(export_module.export_bp)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_export_units_excel_response(monkeypatch, client):
    # Two example rows: one rented, one sold
    rows = [
        {
            "unit_number": "101",
            "unit_size": "500 sqft",
            "ownership_type": "rented",
            "is_special": 1,
            "owner_name": "Alice",
            "monthly_rent": 1200,
            "end_date": "2025-12-31"
        },
        {
            "unit_number": "102",
            "unit_size": "600 sqft",
            "ownership_type": "sold",
            "is_special": 0,
            "owner_name": None,
            "monthly_rent": None,
            "end_date": None
        },
    ]
    dummy_db = DummyDB(rows=rows)
    # Patch get_db in the export module
    monkeypatch.setattr(export_module, 'get_db', lambda: dummy_db)

    resp = client.get('/units/export')
    assert resp.status_code == 200

    # Verify headers
    assert resp.headers["Content-Type"] == \
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    cd = resp.headers.get("Content-Disposition", "")
    assert "attachment" in cd
    assert "units_overview.xlsx" in cd

    # Excel files are ZIP under the hood: should start with PK
    assert resp.data[:2] == b'PK'
