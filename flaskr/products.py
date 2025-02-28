"""
Products module for listing and searching products.

Allows filtering by search query and optional category ID,
then displays the results on a homepage template.
"""

from typing import Dict, List, Any

from flask import Blueprint, render_template, request

from flaskr.db import get_db


products_bp = Blueprint("products", __name__)


@products_bp.route("/products", methods=["GET"])
def list_products() -> str:
    """
    Fetch and display products based on search query and/or category ID.

    Returns:
        str: The rendered HTML of the products homepage with filtered product list.
    """
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
