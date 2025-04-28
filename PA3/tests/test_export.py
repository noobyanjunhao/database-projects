"""Test cases for unit export functionality."""

from typing import Any

from flask.testing import FlaskClient

from flaskr.views import export as export_module  # pylint: disable=import-error


class DummyCursor: # pylint: disable=too-few-public-methods
    """A dummy database cursor that returns preloaded rows."""
    def __init__(self, rows: list[dict[str, Any]]):
        self._rows = rows

    def fetchall(self) -> list[dict[str, Any]]:
        """Return all dummy rows."""
        return self._rows


class DummyDB: # pylint: disable=too-few-public-methods
    """A dummy database connection that simulates queries."""
    def __init__(self, rows: list[dict[str, Any]]):
        self.rows = rows

    def execute(self, query: str) -> DummyCursor:  # pylint: disable=unused-argument
        """Return dummy cursor regardless of the query."""
        return DummyCursor(self.rows)


def test_export_units_excel_response(monkeypatch: Any, client: FlaskClient) -> None:
    """Test that exporting units returns a valid Excel file."""
    rows = [
        {
            "unit_number": "101",
            "unit_size": "500 sqft",
            "ownership_type": "rented",
            "is_special": 1,
            "owner_name": "Alice",
            "monthly_rent": 1200,
            "end_date": "2025-12-31",
        },
        {
            "unit_number": "102",
            "unit_size": "600 sqft",
            "ownership_type": "sold",
            "is_special": 0,
            "owner_name": None,
            "monthly_rent": None,
            "end_date": None,
        },
    ]
    dummy_db = DummyDB(rows)
    monkeypatch.setattr(export_module, "get_db", lambda: dummy_db)

    resp = client.get("/units/export")
    assert resp.status_code == 200
    assert (
        resp.headers["Content-Type"]
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    cd = resp.headers["Content-Disposition"]
    assert "attachment" in cd and "units_overview.xlsx" in cd
    assert resp.data[:2] == b"PK"
