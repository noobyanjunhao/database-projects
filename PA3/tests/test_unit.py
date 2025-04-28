"""Test cases for unit-related views."""

import datetime
from typing import Any, Optional

import pytest
from flask.testing import FlaskClient

from flaskr.views import unit as unit_module  # pylint: disable=import-error


class DummyCursor:
    """A dummy cursor for simulating database results."""

    def __init__(self, rows: list[dict[str, Any]]):
        self._rows = rows

    def fetchall(self) -> list[dict[str, Any]]:
        """Fetch all rows."""
        return self._rows

    def fetchone(self) -> Optional[dict[str, Any]]:
        """Fetch the first row or None if no rows."""
        return self._rows[0] if self._rows else None


class DummyDB:
    """A dummy database connection."""

    def __init__(self, rows: list[dict[str, Any]] | None = None):
        self.rows = rows or []
        self.committed = False

    def execute(self, query: str, args: Any = None) -> DummyCursor:  # pylint: disable=unused-argument
        """Execute a dummy query."""
        return DummyCursor(self.rows)

    def commit(self) -> None:
        """Mark the database as committed."""
        self.committed = True


class SeqDB(DummyDB):  # pylint: disable=super-init-not-called
    """A dummy DB that returns results sequentially."""

    def __init__(self, seq: list[Any]):
        super().__init__([])
        self._seq = list(seq)
        self.committed = False

    def execute(self, query: str, args: Any = None) -> DummyCursor:  # pylint: disable=unused-argument
        """Pop and return the next query result."""
        return DummyCursor(self._seq.pop(0))

    def commit(self) -> None:
        """Mark the database as committed."""
        self.committed = True


@pytest.mark.parametrize("qs", ["", "?search=alice", "?ownership=sold", "?special=1"])
def test_units_overview_branches(
    monkeypatch: Any, client: FlaskClient, qs: str
) -> None:
    """Test units overview with different query strings."""
    rows = [
        {
            "apartment_id": 1,
            "unit_number": "101",
            "unit_size": "100",
            "ownership_type": "rented",
            "is_special": 0,
            "has_lease": 0,
            "tenant_name": "A",
            "monthly_rent": 500,
            "end_date": None,
        }
    ]
    db = DummyDB(rows=rows)
    monkeypatch.setattr(unit_module, "get_db", lambda: db)
    resp = client.get(f"/units{qs}")
    assert resp.status_code == 200
    assert "101" in resp.get_data(as_text=True)


def test_unit_detail_and_balance(monkeypatch: Any, client: FlaskClient) -> None:
    """Test unit detail view and balance calculation."""
    # not found
    db = SeqDB([[]])
    monkeypatch.setattr(unit_module, "get_db", lambda: db)
    assert client.get("/unit/99").status_code == 404

    # valid path + invalid JSON to hit except branch
    lease = [
        {
            "apartment_id": 2,
            "unit_number": "102",
            "unit_size": "200",
            "ownership_type": "sold",
            "is_special": 0,
            "full_name": "B",
            "email": "b@x",
            "monthly_rent": 800,
            "start_date": datetime.datetime(2025, 1, 1),
            "end_date": datetime.datetime(2025, 12, 31),
            "lease_id": 2,
        }
    ]
    seq = [
        lease,  # lease_info
        [],
        [],
        [],  # bills, all_bills, bill_options
        [],
        [],  # payments, all_payments
        [
            {"rent_amount": 800, "other_charges": "not-a-json"}
        ],  # all_bills_calc, triggers except
    ]
    db = SeqDB(seq)
    monkeypatch.setattr(unit_module, "get_db", lambda: db)
    resp = client.get("/unit/2")
    assert resp.status_code == 200
    assert "102" in resp.get_data(as_text=True)


def test_update_lease_paths(monkeypatch: Any, client: FlaskClient) -> None:
    """Test lease update logic."""
    # missing
    db = DummyDB(rows=[])
    monkeypatch.setattr(unit_module, "get_db", lambda: db)
    assert client.post("/unit/99/update-lease", json={}).status_code == 404

    # success
    lease = [{"lease_id": 3, "tenant_id": 4}]
    db = SeqDB([lease, [], [], []])
    monkeypatch.setattr(unit_module, "get_db", lambda: db)
    payload = {
        "tenant_name": "X",
        "tenant_email": "x@x",
        "start_date": "2025-01-01",
        "end_date": "2025-12-31",
        "monthly_rent": 600,
        "ownership_type": "sold",
        "is_special": 1,
    }
    resp = client.post("/unit/3/update-lease", json=payload)
    assert resp.status_code == 200 and db.committed


def test_dummydb_commit_sets_flag() -> None:
    """Test DummyDB commit flag is set."""
    dummy = DummyDB(rows=[])
    assert not dummy.committed
    dummy.commit()
    assert dummy.committed
