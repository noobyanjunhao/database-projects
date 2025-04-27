import sqlite3
import os
from flask import current_app, g, Flask
from flask.cli import with_appcontext
import click
from typing import Optional, Any, Callable, TypeVar, cast, Union

def get_db() -> sqlite3.Connection:
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e: Optional[Exception] = None) -> None:
    db = g.pop('db', None)
    if db is not None:
        db.close()

# def init_db():
#     db = get_db()
#     with current_app.open_resource('schema.sql') as f:
#         db.executescript(f.read().decode('utf8'))

def init_db() -> None:
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        content = f.read()
        if isinstance(content, bytes):
            db.executescript(content.decode("utf8"))
        else:
            db.executescript(content)
    with current_app.open_resource("seed.sql") as f:
        content = f.read()
        if isinstance(content, bytes):
            db.executescript(content.decode("utf8"))
        else:
            db.executescript(content)

@click.command('init-db')
@with_appcontext
def init_db_command() -> None:
    """CLI: Initialize the Database"""
    init_db()
    click.echo('Initialized the database.')

def init_app(app: Flask) -> None:
    app.teardown_appcontext(cast(Callable[[Optional[Exception]], None], close_db))
    app.cli.add_command(init_db_command)
