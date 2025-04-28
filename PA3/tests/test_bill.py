import datetime
import json
import os
import sqlite3
import sys
from typing import Any, Generator, Optional

import pytest
from flask import Flask
from flask.testing import FlaskClient

# Ensure project root is on the import path so we can import flaskr
sys.path.insert(0, os.getcwd())

import flaskr.views.bill as bill_module
# Import blueprints
import flaskr.views.main as main_module
import flaskr.views.unit as unit_module

main_bp = main_module.main_bp
unit_bp = unit_module.unit_bp
bill_bp = bill_module.bill_bp


class DummyCursor:
    def __init__(self, rows: list[dict[str, Any]]):
        self._rows = rows

    def fetchall(self) -> list[dict[str, Any]]:
        return self._rows

    def fetchone(self) -> Optional[dict[str, Any]]:
        return self._rows[0] if self._rows else None


class DummyDB:
    def __init__(self, rows: list[dict[str, Any]] | None = None, fail: bool = False):
        self.rows = rows or []
        self.fail = fail
        self.committed = False

    def execute(self, query: str, args: Any = None) -> DummyCursor:
        if self.fail:
            raise sqlite3.DatabaseError("Simulated DB error")
        return DummyCursor(self.rows)

    def commit(self) -> None:
        self.committed = True


@pytest.fixture
def app() -> Flask:
    # Point Flask at the real templates folder so render_template() works
    templates_path = os.path.join(os.getcwd(), "flaskr", "templates")
    app = Flask(__name__, template_folder=templates_path)
    # Register blueprints for URL building in templates
    app.register_blueprint(main_bp)
    app.register_blueprint(unit_bp)
    app.register_blueprint(bill_bp)
    return app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.mark.parametrize(
    "qs",
    [
        "",
        "?search=alice",
        "?ownership=sold",
        "?special=1",
    ],
)
def test_bill_payment_dashboard_filters(
    monkeypatch: Any, client: FlaskClient, qs: str
) -> None:
    # Our DummyDB returns both rows every time;
    # post-filtering always drops the 'sold' row (101) and keeps the other (102).
    rows = [
        {
            "apartment_id": 1,
            "unit_number": "101",
            "ownership_type": "sold",
            "is_special": 0,
            "full_name": "Alice",
        },
        {
            "apartment_id": 2,
            "unit_number": "102",
            "ownership_type": "rent_controlled",
            "is_special": 1,
            "full_name": "Bob",
        },
    ]
    dummy = DummyDB(rows=rows)
    monkeypatch.setattr(bill_module, "get_db", lambda: dummy)

    resp = client.get(f"/bill-payment{qs}")
    assert resp.status_code == 200
    text = resp.get_data(as_text=True)

    # '101' should always be filtered out (sold), and '102' always shown
    assert "102" in text
    assert "101" not in text


def test_create_and_detail_and_payment_paths(
    monkeypatch: Any, client: FlaskClient
) -> None:
    # create-bill not found
    dummy = DummyDB(rows=[])
    monkeypatch.setattr(bill_module, "get_db", lambda: dummy)
    r1 = client.post(
        "/unit/99/create-bill",
        json={
            "billing_month": "2025-05",
            "rent_amount": 1000,
            "other_charges": {},
            "balance_used": 0,
            "total_amount": 1000,
        },
    )
    assert r1.status_code == 404

    # create-bill success
    lease = {"lease_id": 10, "email": "a@b.com", "full_name": "Abc"}
    dummy = DummyDB(rows=[lease])
    monkeypatch.setattr(bill_module, "get_db", lambda: dummy)
    r2 = client.post(
        "/unit/1/create-bill",
        json={
            "billing_month": "2025-06",
            "rent_amount": 1500,
            "other_charges": {"x": 50},
            "balance_used": 100,
            "total_amount": 1450,
        },
    )
    assert r2.status_code == 200
    assert dummy.committed

    # bill-detail not found
    dummy = DummyDB(rows=[])
    monkeypatch.setattr(bill_module, "get_db", lambda: dummy)
    r3 = client.get("/bill/999")
    assert r3.status_code == 404

    # bill-detail success (valid JSON)
    bill_row = {
        "sent_at": datetime.datetime(2025, 6, 1),
        "billing_month": "2025-06",
        "rent_amount": 1500,
        "other_charges": json.dumps({"water": 30}),
        "balance_used": 0,
        "total_amount": 1530,
        "full_name": "Zed",
        "unit_number": "U8",
        "apartment_id": 8,
    }
    dummy = DummyDB(rows=[bill_row])
    monkeypatch.setattr(bill_module, "get_db", lambda: dummy)
    r4 = client.get("/bill/8")
    assert r4.status_code == 200
    assert "U8" in r4.get_data(as_text=True)

    # bill-detail success (invalid JSON)
    bad_row = bill_row.copy()
    bad_row["other_charges"] = "not-json"
    bad_row["unit_number"] = "U9"
    bad_row["apartment_id"] = 9
    dummy = DummyDB(rows=[bad_row])
    monkeypatch.setattr(bill_module, "get_db", lambda: dummy)
    r5 = client.get("/bill/9")
    assert r5.status_code == 200
    assert "U9" in r5.get_data(as_text=True)

    # create-payment missing fields
    dummy = DummyDB()
    monkeypatch.setattr(bill_module, "get_db", lambda: dummy)
    r6 = client.post("/unit/1/create-payment", json={})
    assert r6.status_code == 400

    # create-payment DB error
    dummy = DummyDB(fail=True)
    monkeypatch.setattr(bill_module, "get_db", lambda: dummy)
    r7 = client.post(
        "/unit/1/create-payment",
        json={
            "bill_id": 1,
            "amount": 100,
            "payment_date": "2025-07-10",
            "check_number": "CHK",
            "remitter_name": "Me",
        },
    )
    assert r7.status_code == 500

    # create-payment success
    dummy = DummyDB()
    monkeypatch.setattr(bill_module, "get_db", lambda: dummy)
    r8 = client.post(
        "/unit/1/create-payment",
        json={
            "bill_id": 2,
            "amount": 200,
            "payment_date": "2025-07-15",
            "check_number": "XYZ",
            "remitter_name": "You",
        },
    )
    assert r8.status_code == 200
    assert dummy.committed

    # payment-detail not found
    dummy = DummyDB(rows=[])
    monkeypatch.setattr(bill_module, "get_db", lambda: dummy)
    r9 = client.get("/payment/1234")
    assert r9.status_code == 404

    # payment-detail success
    payment_row = {
        "id": 3,
        "bill_id": 2,
        "amount": 250,
        "payment_date": datetime.datetime(2025, 7, 20),
        "check_number": "PMT",
        "remitter_name": "Bob",
        "unit_number": "U10",
        "apartment_id": 10,
        "full_name": "Bob",
    }
    dummy = DummyDB(rows=[payment_row])
    monkeypatch.setattr(bill_module, "get_db", lambda: dummy)
    r10 = client.get("/payment/3")
    assert r10.status_code == 200
    assert "U10" in r10.get_data(as_text=True)
