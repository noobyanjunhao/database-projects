import sqlite3
import click
from flask import g, current_app
from flask.cli import with_appcontext

DATABASE = "northwind.db"  # 继续使用原来的 northwind 数据库

def get_db() -> sqlite3.Connection:
    """获取数据库连接"""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # 让查询结果支持字典访问
    return g.db

def close_db(e=None) -> None:
    """关闭数据库连接"""
    db = g.pop("db", None)
    if db is not None:
        db.close()

def update_db() -> None:
    """只执行 schema.sql 以新增表，不影响已有数据"""
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))
    click.echo("✅ Database updated successfully. (New tables added)")

@click.command("update-db")
@with_appcontext
def update_db_command():
    """Flask CLI 命令: 只创建新表，不删除已有数据"""
    update_db()

def init_app(app):
    """注册数据库相关的函数"""
    app.teardown_appcontext(close_db)
    app.cli.add_command(update_db_command)  # 注册 `flask update-db` 命令

