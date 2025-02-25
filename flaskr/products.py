from flask import Blueprint, render_template, request
from flaskr.db import get_db
from typing import Dict, List, Any

products_bp = Blueprint("products", __name__)

@products_bp.route("/products", methods=["GET"])
def list_products() -> str:
    db = get_db()

    search_query: str = request.args.get("search", "").strip()
    category_id: str = request.args.get("category", "").strip()

    sql_query: str = "SELECT * FROM Products WHERE 1=1"
    params: Dict[str, str] = {}

    if search_query:
        sql_query += " AND ProductName LIKE :search"
        params["search"] = f"%{search_query}%"

    if category_id.isdigit():
        sql_query += " AND CategoryID = :category"
        params["category"] = str(int(category_id))

    products = db.execute(sql_query, params).fetchall()
    products_list: List[Dict[str, Any]] = [dict(row) for row in products]
    
    return render_template("products/homepage.html", products=products_list)
