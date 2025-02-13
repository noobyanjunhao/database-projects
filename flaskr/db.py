import sqlite3
from flask import g, current_app

DATABASE = "northwind.db"  # 继续使用 Northwind 数据库

def get_db() -> sqlite3.Connection:
    """获取 SQLite 数据库连接"""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # 让查询结果支持字典访问
    return g.db

def close_db(e=None) -> None:
    """关闭数据库连接"""
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_app(app):
    """注册数据库相关的函数"""
    app.teardown_appcontext(close_db)
