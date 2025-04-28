"""Database utility functions for the Flask app."""
import sqlite3
from typing import  Optional

import click
from flask import Flask, current_app, g
from flask.cli import with_appcontext


def get_db() -> sqlite3.Connection:
    """Get a database connection, create one if not exists."""
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(_e: Optional[Exception] = None) -> None:
    """Close the database connection if it exists."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    """Initialize the database schema and seed data."""
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


@click.command("init-db")
@with_appcontext
def init_db_command() -> None:
    """Flask CLI command to initialize the database."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app: Flask) -> None:
    """Register database functions with the Flask app."""
    def teardown(_: Optional[BaseException] = None) -> None:
        close_db()

    app.teardown_appcontext(teardown)
    app.cli.add_command(init_db_command)
