"""Unit management views."""
import json
from typing import Any, Dict, Tuple, Union

from flask import Blueprint, render_template, request

from flaskr.db import get_db

unit_bp = Blueprint("unit", __name__)


@unit_bp.route("/units")
def units_overview() -> str:
    """Display a list of all units with optional filters."""
    db = get_db()
    special_only: bool = request.args.get("special") == "1"
    ownership: str = request.args.get("ownership", "")
    search: str = request.args.get("search", "").lower()

    query: str = """
        SELECT
        A.id            AS apartment_id,
        A.unit_number,
        A.unit_size,
        A.ownership_type,
        A.is_special,
        CASE WHEN L.id IS NOT NULL THEN 1 ELSE 0 END AS has_lease,
        T.full_name     AS tenant_name,
        L.monthly_rent,
        L.end_date
        FROM Apartment A
        LEFT JOIN Lease   L ON L.apartment_id = A.id
        LEFT JOIN Tenant  T ON T.id = L.tenant_id
        WHERE 1=1
    """
    args: list[str] = []

    if search:
        query += " AND (LOWER(A.unit_number) LIKE ? OR LOWER(T.full_name) LIKE ?)"
        args.extend([f"%{search}%", f"%{search}%"])
    if ownership:
        query += " AND A.ownership_type = ?"
        args.append(ownership)
    if special_only:
        query += " AND A.is_special = 1"

    data = db.execute(query, args).fetchall()
    return render_template("units_overview.html", data=data)


@unit_bp.route("/unit/<int:unit_id>")
def unit_detail(unit_id: int) -> Union[str, Tuple[str, int]]: # pylint: disable=too-many-locals
    """Display detailed information about a specific unit."""
    db = get_db()
    lease_info = db.execute(
        """
        SELECT A.id AS apartment_id, A.unit_number, A.unit_size, A.ownership_type, A.is_special,
            T.full_name, T.email,
            L.monthly_rent, L.start_date, L.end_date, L.id AS lease_id
        FROM Apartment A
        JOIN Lease L ON L.apartment_id = A.id
        JOIN Tenant T ON T.id = L.tenant_id
        WHERE A.id = ?
        ORDER BY L.start_date DESC LIMIT 1
    """,
        (unit_id,),
    ).fetchone()

    if lease_info is None:
        return f"No lease data found for unit {unit_id}", 404

    if lease_info["ownership_type"].lower() == "sold":
        lease_info["monthly_rent"] = 0.0

    lease_id = lease_info["lease_id"]

    bills = db.execute(
        """
        SELECT id, sent_at, total_amount
        FROM Bill
        WHERE lease_id = ?
        ORDER BY sent_at DESC
        LIMIT 6
    """,
        (lease_id,),
    ).fetchall()

    all_bills = db.execute(
        """
        SELECT id, sent_at, total_amount
        FROM Bill
        WHERE lease_id = ?
        ORDER BY sent_at DESC
    """,
        (lease_id,),
    ).fetchall()

    bill_options = db.execute(
        """
        SELECT id, billing_month, rent_amount, total_amount
        FROM Bill
        WHERE lease_id = ?
        ORDER BY billing_month DESC
    """,
        (lease_id,),
    ).fetchall()

    bill_years = sorted(set(b["sent_at"].year for b in all_bills))

    payments = db.execute(
        """
        SELECT id, payment_date, amount
        FROM Payment
        WHERE bill_id IN (
            SELECT id FROM Bill WHERE lease_id = ?
        )
        ORDER BY payment_date DESC
        LIMIT 6
    """,
        (lease_id,),
    ).fetchall()

    all_payments = db.execute(
        """
        SELECT id, payment_date, amount
        FROM Payment
        WHERE bill_id IN (
            SELECT id FROM Bill WHERE lease_id = ?
        )
        ORDER BY payment_date DESC
    """,
        (lease_id,),
    ).fetchall()

    payment_years = sorted(set(p["payment_date"].year for p in all_payments))
    all_bills_calc = db.execute(
        "SELECT rent_amount, other_charges FROM Bill WHERE lease_id = ?", (lease_id,)
    ).fetchall()

    total_due: float = 0.0
    for bill in all_bills_calc:
        total_due += bill["rent_amount"]
        if bill["other_charges"]:
            try:
                charges: Dict[str, float] = json.loads(bill["other_charges"])
                total_due += sum(float(v) for v in charges.values())  # pragma: no cover
            except json.JSONDecodeError:  # pragma: no cover
                pass  # pragma: no cover

    total_paid: float = sum(p["amount"] for p in all_payments)
    balance: float = round(total_paid - total_due, 2)

    return render_template(
        "unit_detail.html",
        lease=lease_info,
        balance=balance,
        bills=bills,
        payments=payments,
        all_bills=all_bills,
        all_payments=all_payments,
        payment_years=payment_years,
        bill_years=bill_years,
        apartment_id=lease_info["apartment_id"],
        bill_options=bill_options,
    )


@unit_bp.route("/unit/<int:unit_id>/update-lease", methods=["POST"])
def update_lease(unit_id: int) -> Tuple[str, int]:
    """Update lease and tenant information for a unit."""
    db = get_db()
    data: Dict[str, Any] = request.get_json()

    lease = db.execute(
        """
        SELECT L.id AS lease_id, T.id AS tenant_id
        FROM Lease L
        JOIN Apartment A ON L.apartment_id = A.id
        JOIN Tenant T ON L.tenant_id = T.id
        WHERE A.id = ?
        ORDER BY L.start_date DESC
        LIMIT 1
    """,
        (unit_id,),
    ).fetchone()

    if not lease:
        return "Lease not found", 404

    db.execute(
        """
        UPDATE Tenant SET full_name = ?, email = ?
        WHERE id = ?
    """,
        (data["tenant_name"], data["tenant_email"], lease["tenant_id"]),
    )

    db.execute(
        """
        UPDATE Lease
        SET start_date = ?, end_date = ?, monthly_rent = ?
        WHERE id = ?
    """,
        (data["start_date"], data["end_date"], data["monthly_rent"], lease["lease_id"]),
    )

    db.execute(
        """
        UPDATE Apartment
        SET ownership_type = ?, is_special = ?
        WHERE id = ?
    """,
        (data["ownership_type"], data["is_special"], unit_id),
    )

    db.commit()
    return "", 200
