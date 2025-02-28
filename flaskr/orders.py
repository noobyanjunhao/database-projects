from flask import Blueprint, render_template, session, redirect, url_for, Response
from werkzeug.wrappers import Response as WerkzeugResponse
from flaskr.db import get_db
from typing import Union, List, Dict, Any

orders_bp = Blueprint("orders", __name__, url_prefix="/orders")

@orders_bp.route("/")
def view_orders() -> Union[str, WerkzeugResponse]:
    """显示当前用户的所有订单"""
    if 'user_id' not in session:
        return redirect(url_for('user.login'))  # 未登录用户跳转到登录页面

    user_id: str = session['user_id']
    db = get_db()

    # 获取当前用户的所有订单
    orders = db.execute("""
        SELECT * FROM Orders WHERE CustomerID = ?
        ORDER BY OrderDate DESC
    """, (user_id,)).fetchall()

    # 转换数据格式，方便在前端使用
    orders_list: List[Dict[str, Any]] = [dict(order) for order in orders]

    return render_template("orders/orders.html", orders=orders_list)

