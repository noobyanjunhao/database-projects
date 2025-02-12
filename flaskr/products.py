from flask import Blueprint, render_template
from flaskr.db import get_db

product_bp = Blueprint("products", __name__)

@products_bp.route("/products", method=["GET"])
def list_products() -> str:
    db = get_db()
    products = db.execute(
        "SELECT ProductID, ProductName, UnitPrice FROM Products"
    ).fetchall()
    return render_template("products/list.html", products=products)
