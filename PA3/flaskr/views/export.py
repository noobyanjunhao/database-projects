from flask import Blueprint, send_file
from flaskr.db import get_db
import pandas as pd
import io

export_bp = Blueprint('export', __name__)

@export_bp.route('/units/export')
def export_units():
    db = get_db()
    units = db.execute("""
        SELECT A.unit_number, A.unit_size, A.ownership_type, A.is_special, 
            T.full_name AS owner_name, 
            L.monthly_rent, L.end_date
        FROM Apartment A
        LEFT JOIN Lease L ON L.apartment_id = A.id
        LEFT JOIN Tenant T ON T.id = L.tenant_id
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



