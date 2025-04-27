# from flask import Blueprint, render_template, request, jsonify
# from flaskr.db import get_db
# import json

# bill_bp = Blueprint('bill', __name__)

# @bill_bp.route('/bill-payment')
# def bill_payment_dashboard():
#     db = get_db()
#     search = request.args.get('search', '').lower()
#     ownership = request.args.get('ownership', '')
#     special_only = request.args.get('special') == '1'

#     query = """
#         SELECT A.id AS apartment_id, A.unit_number, A.ownership_type, A.is_special, T.full_name
#         FROM Apartment A
#         JOIN Lease L ON L.apartment_id = A.id
#         JOIN Tenant T ON T.id = L.tenant_id
#         WHERE 1=1
#     """

#     args = []

#     if search:
#         query += " AND (LOWER(A.unit_number) LIKE ? OR LOWER(T.full_name) LIKE ?)"
#         args.extend([f"%{search}%", f"%{search}%"])

#     if ownership:
#         query += " AND A.ownership_type = ?"
#         args.append(ownership)

#     if special_only:
#         query += " AND A.is_special = 1"

#     data = db.execute(query, args).fetchall()
#     filtered_data = []
#     for row in data:
#         if row['ownership_type'] == 'sold':
#             continue
#         if row['full_name'] is None:
#             continue # pragma: no cover
#         filtered_data.append(row)

#     return render_template('bill_payment.html', data=filtered_data)


# @bill_bp.route('/unit/<int:unit_id>/create-bill', methods=['POST'])
# def create_bill(unit_id):
#     db = get_db()
#     data = request.get_json()

#     lease = db.execute("""
#         SELECT L.id AS lease_id, T.email, T.full_name
#         FROM Lease L
#         JOIN Apartment A ON L.apartment_id = A.id
#         JOIN Tenant T ON T.id = L.tenant_id
#         WHERE A.id = ?
#         ORDER BY L.start_date DESC
#         LIMIT 1
#     """, (unit_id,)).fetchone()

#     if not lease:
#         return "Lease not found", 404

#     db.execute("""
#         INSERT INTO Bill (lease_id, billing_month, rent_amount, other_charges, balance_used, total_amount)
#         VALUES (?, ?, ?, ?, ?, ?)
#     """, (
#         lease["lease_id"],
#         data["billing_month"] + "-01",
#         data["rent_amount"],
#         json.dumps(data["other_charges"]),
#         data["balance_used"],
#         data["total_amount"]
#     ))
#     db.commit()

#     print("📧 Simulated Email Sent")
#     print("To:", lease["email"])
#     print("Subject: New Rent Bill Issued")
#     print(f"Dear {lease['full_name']},")
#     print(f"Here is your bill for {data['billing_month']}:")
#     print(f" - Rent: ${data['rent_amount']:.2f}")
#     print(f" - Other Charges: {data['other_charges']}")
#     print(f" - Balance Used: ${data['balance_used']:.2f}")
#     print(f" - Total Due: ${data['total_amount']:.2f}")

#     return "", 200


# @bill_bp.route('/bill/<int:bill_id>')
# def bill_detail(bill_id):
#     db = get_db()
#     bill = db.execute("""
#         SELECT B.sent_at, B.billing_month, B.rent_amount, B.other_charges, B.balance_used, B.total_amount,
#             T.full_name, A.unit_number, A.id AS apartment_id
#         FROM Bill B
#         JOIN Lease L ON B.lease_id = L.id
#         JOIN Tenant T ON L.tenant_id = T.id
#         JOIN Apartment A ON L.apartment_id = A.id
#         WHERE B.id = ?
#     """, (bill_id,)).fetchone()

#     if not bill:
#         return "Bill not found", 404

#     # Parse other_charges JSON
#     charges = {}
#     if bill["other_charges"]:
#         try:
#             charges = json.loads(bill["other_charges"])
#         except:  # pragma: no cover
#             charges = {}

#     return render_template("bill_detail.html", bill=bill, charges=charges, apartment_id=bill['apartment_id'])


# @bill_bp.route('/unit/<int:unit_id>/create-payment', methods=['POST'])
# def create_payment(unit_id):
#     db = get_db()
#     data = request.get_json()

#     required_fields = ['bill_id', 'amount', 'payment_date', 'check_number', 'remitter_name']
#     if not all(field in data and data[field] for field in required_fields):
#         return "Missing required fields", 400

#     try:
#         db.execute("""
#             INSERT INTO Payment (bill_id, amount, payment_date, check_number, remitter_name)
#             VALUES (?, ?, ?, ?, ?)
#         """, (
#             data["bill_id"],
#             data["amount"],
#             data["payment_date"],
#             data["check_number"],
#             data["remitter_name"]
#         ))
#         db.commit()
#         return "", 200
#     except Exception as e:
#         print("Payment Insert Error:", e)
#         return "Database error", 500


# @bill_bp.route('/payment/<int:payment_id>')
# def payment_detail(payment_id):
#     db = get_db()
#     payment = db.execute("""
#         SELECT P.*, A.unit_number, A.id AS apartment_id, T.full_name
#         FROM Payment P
#         JOIN Bill B ON P.bill_id = B.id
#         JOIN Lease L ON B.lease_id = L.id
#         JOIN Apartment A ON L.apartment_id = A.id
#         JOIN Tenant T ON L.tenant_id = T.id
#         WHERE P.id = ?
#     """, (payment_id,)).fetchone()

#     if not payment:
#         return "Payment not found", 404

#     return render_template("payment_detail.html", payment=payment, apartment_id=payment['apartment_id'])


from flask import Blueprint, render_template, request, jsonify
from flaskr.db import get_db
import json
from typing import Any, Dict, Tuple, Union

bill_bp = Blueprint('bill', __name__)

@bill_bp.route('/bill-payment')
def bill_payment_dashboard() -> str:
    db = get_db()
    search: str = request.args.get('search', '').lower()
    ownership: str = request.args.get('ownership', '')
    special_only: bool = request.args.get('special') == '1'

    query: str = """
        SELECT A.id AS apartment_id, A.unit_number, A.ownership_type, A.is_special, T.full_name
        FROM Apartment A
        JOIN Lease L ON L.apartment_id = A.id
        JOIN Tenant T ON T.id = L.tenant_id
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
    filtered_data: list[Any] = []
    for row in data:
        if row['ownership_type'] == 'sold':
            continue
        if row['full_name'] is None:
            continue  # pragma: no cover
        filtered_data.append(row)

    return render_template('bill_payment.html', data=filtered_data)


@bill_bp.route('/unit/<int:unit_id>/create-bill', methods=['POST'])
def create_bill(unit_id: int) -> Tuple[str, int]:
    db = get_db()
    data: Dict[str, Any] = request.get_json()

    lease = db.execute("""
        SELECT L.id AS lease_id, T.email, T.full_name
        FROM Lease L
        JOIN Apartment A ON L.apartment_id = A.id
        JOIN Tenant T ON T.id = L.tenant_id
        WHERE A.id = ?
        ORDER BY L.start_date DESC
        LIMIT 1
    """, (unit_id,)).fetchone()

    if not lease:
        return "Lease not found", 404

    db.execute("""
        INSERT INTO Bill (lease_id, billing_month, rent_amount, other_charges, balance_used, total_amount)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        lease["lease_id"],
        data["billing_month"] + "-01",
        data["rent_amount"],
        json.dumps(data["other_charges"]),
        data["balance_used"],
        data["total_amount"]
    ))
    db.commit()

    print("Simulated Email Sent")
    print("To:", lease["email"])
    print("Subject: New Rent Bill Issued")
    print(f"Dear {lease['full_name']},")
    print(f"Here is your bill for {data['billing_month']}:")
    print(f" - Rent: ${data['rent_amount']:.2f}")
    print(f" - Other Charges: {data['other_charges']}")
    print(f" - Balance Used: ${data['balance_used']:.2f}")
    print(f" - Total Due: ${data['total_amount']:.2f}")

    return "", 200


@bill_bp.route('/bill/<int:bill_id>')
def bill_detail(bill_id: int) -> Union[str, Tuple[str, int]]:
    db = get_db()
    bill = db.execute("""
        SELECT B.sent_at, B.billing_month, B.rent_amount, B.other_charges, B.balance_used, B.total_amount,
            T.full_name, A.unit_number, A.id AS apartment_id
        FROM Bill B
        JOIN Lease L ON B.lease_id = L.id
        JOIN Tenant T ON L.tenant_id = T.id
        JOIN Apartment A ON L.apartment_id = A.id
        WHERE B.id = ?
    """, (bill_id,)).fetchone()

    if not bill:
        return "Bill not found", 404

    charges: Dict[str, Any] = {}
    if bill["other_charges"]:
        try:
            charges = json.loads(bill["other_charges"])
        except Exception:  # pragma: no cover
            charges = {}

    return render_template("bill_detail.html", bill=bill, charges=charges, apartment_id=bill['apartment_id'])


@bill_bp.route('/unit/<int:unit_id>/create-payment', methods=['POST'])
def create_payment(unit_id: int) -> Tuple[str, int]:
    db = get_db()
    data: Dict[str, Any] = request.get_json()

    required_fields: list[str] = ['bill_id', 'amount', 'payment_date', 'check_number', 'remitter_name']
    if not all(field in data and data[field] for field in required_fields):
        return "Missing required fields", 400

    try:
        db.execute("""
            INSERT INTO Payment (bill_id, amount, payment_date, check_number, remitter_name)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data["bill_id"],
            data["amount"],
            data["payment_date"],
            data["check_number"],
            data["remitter_name"]
        ))
        db.commit()
        return "", 200
    except Exception as e:
        print("Payment Insert Error:", e)
        return "Database error", 500


@bill_bp.route('/payment/<int:payment_id>')
def payment_detail(payment_id: int) -> Union[str, Tuple[str, int]]:
    db = get_db()
    payment = db.execute("""
        SELECT P.*, A.unit_number, A.id AS apartment_id, T.full_name
        FROM Payment P
        JOIN Bill B ON P.bill_id = B.id
        JOIN Lease L ON B.lease_id = L.id
        JOIN Apartment A ON L.apartment_id = A.id
        JOIN Tenant T ON L.tenant_id = T.id
        WHERE P.id = ?
    """, (payment_id,)).fetchone()

    if not payment:
        return "Payment not found", 404

    return render_template("payment_detail.html", payment=payment, apartment_id=payment['apartment_id'])
