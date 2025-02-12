from flask import Blueprint, render_template
from flaskr.db import get_db

products_bp = Blueprint("products", __name__)

@products_bp.route("/products", methods=["GET"])
def list_products() -> str:
    db = get_db()
    products = db.execute(
        "SELECT ProductID, ProductName, UnitPrice FROM Products"
    ).fetchall()
    products_list = [dict(product) for product in products]

    print("product information:", products_list)

    return render_template("products/homepage.html", products=products_list)
