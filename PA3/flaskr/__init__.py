import os
from flask import Flask, render_template, request
from .db import get_db
from datetime import datetime
import json
import io
import pandas as pd
from flask import send_file

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite')
    )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    if not os.path.exists(app.config['DATABASE']):
        with app.app_context():
            db.init_db()

    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/bill-payment')
    def bill_payment_dashboard():
        db = get_db()

        search = request.args.get('search', '').lower()
        ownership = request.args.get('ownership', '')
        special_only = request.args.get('special') == '1'

        query = """
            SELECT A.id AS apartment_id, A.unit_number, A.ownership_type, A.is_special, T.full_name
            FROM Apartment A
            JOIN Lease L ON L.apartment_id = A.id
            JOIN Tenant T ON T.id = L.tenant_id
            WHERE 1=1
        """

        args = []

        if search:
            query += " AND (LOWER(A.unit_number) LIKE ? OR LOWER(T.full_name) LIKE ?)"
            args.extend([f"%{search}%", f"%{search}%"])

        if ownership:
            query += " AND A.ownership_type = ?"
            args.append(ownership)

        if special_only:
            query += " AND A.is_special = 1"

        data = db.execute(query, args).fetchall()
        filtered_data = []
        for row in data:
            if row['ownership_type'] == 'sold':
                continue
            if row['full_name'] is None:
                continue
            filtered_data.append(row)

        return render_template('bill_payment.html', data=filtered_data)
    
    @app.route('/unit/<int:unit_id>')
    def unit_detail(unit_id):

        db = get_db()

        lease_info = db.execute("""
            SELECT A.id AS apartment_id, A.unit_number, A.unit_size, A.ownership_type, A.is_special,
                T.full_name, T.email,
                L.monthly_rent, L.start_date, L.end_date, L.id AS lease_id
            FROM Apartment A
            JOIN Lease L ON L.apartment_id = A.id
            JOIN Tenant T ON T.id = L.tenant_id
            WHERE A.id = ?
            ORDER BY L.start_date DESC LIMIT 1
        """, (unit_id,)).fetchone()

        if lease_info is None:
            return f"No lease data found for unit {unit_id}", 404
        
        if lease_info["ownership_type"].lower() == "sold":
            lease_info["monthly_rent"] = 0.0

        lease_id = lease_info["lease_id"]


        bills = db.execute("""
            SELECT id, sent_at, total_amount
            FROM Bill
            WHERE lease_id = ?
            ORDER BY sent_at DESC
            LIMIT 6
        """, (lease_id,)).fetchall()


        all_bills = db.execute("""
            SELECT id, sent_at, total_amount
            FROM Bill
            WHERE lease_id = ?
            ORDER BY sent_at DESC
        """, (lease_id,)).fetchall()

        bill_options = db.execute("""
            SELECT id, billing_month, rent_amount, total_amount
            FROM Bill
            WHERE lease_id = ?
            ORDER BY billing_month DESC
        """, (lease_id,)).fetchall()


        bill_years = sorted(set(b["sent_at"].year for b in all_bills))

        payments = db.execute("""
            SELECT id, payment_date, amount
            FROM Payment
            WHERE bill_id IN (
                SELECT id FROM Bill WHERE lease_id = ?
            )
            ORDER BY payment_date DESC
            LIMIT 6
        """, (lease_id,)).fetchall()

        

        all_payments = db.execute("""
            SELECT id, payment_date, amount
            FROM Payment
            WHERE bill_id IN (
                SELECT id FROM Bill WHERE lease_id = ?
            )
            ORDER BY payment_date DESC
        """, (lease_id,)).fetchall()

        payment_years = sorted(set(p["payment_date"].year for p in all_payments))
        all_bills_calc = db.execute("SELECT rent_amount, other_charges FROM Bill WHERE lease_id = ?", (lease_id,)).fetchall()
        # all_payments = db.execute("SELECT amount FROM Payment WHERE bill_id IN (SELECT id FROM Bill WHERE lease_id = ?)", (lease_id,)).fetchall()

        total_due = 0.0
        for bill in all_bills_calc:
            total_due += bill["rent_amount"]
            if bill["other_charges"]:
                try:
                    charges = json.loads(bill["other_charges"])
                    total_due += sum(float(v) for v in charges.values())
                except:
                    pass
        total_paid = sum(p["amount"] for p in all_payments)
        balance = round(total_paid - total_due, 2)

        return render_template("unit_detail.html", lease=lease_info, balance=balance, bills=bills, payments=payments, all_bills=all_bills, all_payments=all_payments, payment_years=payment_years, bill_years=bill_years, apartment_id=lease_info["apartment_id"], bill_options=bill_options)



    @app.route('/unit/<int:unit_id>/create-bill', methods=['POST'])
    def create_bill(unit_id):
        db = get_db()
        data = request.get_json()

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

        print("📧 Simulated Email Sent")
        print("To:", lease["email"])
        print("Subject: New Rent Bill Issued")
        print(f"Dear {lease['full_name']},")
        print(f"Here is your bill for {data['billing_month']}:")
        print(f" - Rent: ${data['rent_amount']:.2f}")
        print(f" - Other Charges: {data['other_charges']}")
        print(f" - Balance Used: ${data['balance_used']:.2f}")
        print(f" - Total Due: ${data['total_amount']:.2f}")

        return "", 200


    @app.route('/bill/<int:bill_id>')
    def bill_detail(bill_id):
        db = get_db()

        bill = db.execute("""
            SELECT B.sent_at, B.billing_month, B.rent_amount, B.other_charges, B.balance_used, B.total_amount,
                T.full_name, A.unit_number
            FROM Bill B
            JOIN Lease L ON B.lease_id = L.id
            JOIN Tenant T ON L.tenant_id = T.id
            JOIN Apartment A ON L.apartment_id = A.id
            WHERE B.id = ?
        """, (bill_id,)).fetchone()

        if not bill:
            return "Bill not found", 404

        # Parse other_charges JSON
        charges = {}
        if bill["other_charges"]:
            try:
                charges = json.loads(bill["other_charges"])
            except:
                charges = {}

        return render_template("bill_detail.html", bill=bill, charges=charges)



    @app.route('/unit/<int:unit_id>/create-payment', methods=['POST'])
    def create_payment(unit_id):
        db = get_db()
        data = request.get_json()

        required_fields = ['bill_id', 'amount', 'payment_date', 'check_number', 'remitter_name']
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


    @app.route('/payment/<int:payment_id>')
    def payment_detail(payment_id):
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

        return render_template("payment_detail.html", payment=payment)


    # @app.route('/units')
    # def units_overview():
    #     db = get_db()

    #     search = request.args.get('search', '').lower()
    #     ownership = request.args.get('ownership', '')
    #     special_only = request.args.get('special') == '1'

    #     query = """
    #         SELECT A.id AS apartment_id, A.unit_number, A.unit_size, A.ownership_type, A.is_special,
    #             T.full_name, L.monthly_rent, L.end_date
    #         FROM Apartment A
    #         LEFT JOIN Lease L ON L.apartment_id = A.id
    #         LEFT JOIN Tenant T ON T.id = L.tenant_id
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
    #     return render_template('units_overview.html', data=data)
    
    @app.route('/units')
    def units_overview():
        db = get_db()

        search = request.args.get('search', '').lower()
        ownership = request.args.get('ownership', '')
        special_only = request.args.get('special') == '1'

        query = """
            SELECT
            A.id            AS apartment_id,
            A.unit_number,
            A.unit_size,
            A.ownership_type,
            A.is_special,
            -- 如果找到了 Lease，就标记为 1，否则为 0
            CASE WHEN L.id IS NOT NULL THEN 1 ELSE 0 END AS has_lease,
            T.full_name     AS tenant_name,
            L.monthly_rent,
            L.end_date
            FROM Apartment A
            LEFT JOIN Lease   L ON L.apartment_id = A.id
            LEFT JOIN Tenant  T ON T.id = L.tenant_id
            WHERE 1=1
        """
        args = []

        if search:
            query += " AND (LOWER(A.unit_number) LIKE ? OR LOWER(T.full_name) LIKE ?)"
            args.extend([f"%{search}%", f"%{search}%"])
        if ownership:
            query += " AND A.ownership_type = ?"
            args.append(ownership)
        if special_only:
            query += " AND A.is_special = 1"

        data = db.execute(query, args).fetchall()
        return render_template('units_overview.html', data=data)


    @app.route('/unit/<int:unit_id>/update-lease', methods=['POST'])
    def update_lease(unit_id):
        db = get_db()
        data = request.get_json()

        lease = db.execute("""
            SELECT L.id AS lease_id, T.id AS tenant_id
            FROM Lease L
            JOIN Apartment A ON L.apartment_id = A.id
            JOIN Tenant T ON L.tenant_id = T.id
            WHERE A.id = ?
            ORDER BY L.start_date DESC
            LIMIT 1
        """, (unit_id,)).fetchone()

        if not lease:
            return "Lease not found", 404

        db.execute("""
            UPDATE Tenant SET full_name = ?, email = ?
            WHERE id = ?
        """, (data['tenant_name'], data['tenant_email'], lease['tenant_id']))

        db.execute("""
            UPDATE Lease
            SET start_date = ?, end_date = ?, monthly_rent = ?
            WHERE id = ?
        """, (data['start_date'], data['end_date'], data['monthly_rent'], lease['lease_id']))

        db.execute("""
            UPDATE Apartment
            SET ownership_type = ?, is_special = ?
            WHERE id = ?
        """, (data['ownership_type'], data['is_special'], unit_id))

        db.commit()
        return "", 200



    @app.route('/units/export')
    def export_units():
        db = get_db()

        units = db.execute("""
            SELECT A.unit_number, A.unit_size, A.ownership_type, A.is_special, 
                T.full_name AS owner_name, 
                L.monthly_rent, L.end_date
            FROM Apartment A
            LEFT JOIN Lease L ON L.apartment_id = A.id
            LEFT JOIN Tenant T ON T.id = L.tenant_id
            WHERE A.ownership_type != 'sold'
            ORDER BY A.unit_number
        """).fetchall()

        data = []
        for u in units:
            data.append({
                "Unit Number": u["unit_number"],
                "Unit Size": u["unit_size"],
                "Ownership Type": u["ownership_type"],
                "Is Special": "Yes" if u["is_special"] else "No",
                "Owner Name": u["owner_name"] or "N/A",
                "Monthly Rent": u["monthly_rent"] if u["ownership_type"] != "sold" else None,
                "Rent End Date": u["end_date"] if u["ownership_type"] != "sold" else None,
            })

        df = pd.DataFrame(data)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name="Units")

        output.seek(0)

        return send_file(
            output,
            as_attachment=True,
            download_name="units_overview.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )




    return app


