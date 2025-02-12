import sqlite3
from flask import g

DATABASE = "northwind.db"

def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()

