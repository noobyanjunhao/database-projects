# # tests/conftest.py

# import os
# import io
# import sys
# import sqlite3
# import pytest
# from flaskr import create_app
# from flaskr.db import get_db, init_db

# # allow top-level imports
# sys.path.insert(0, os.getcwd())

# @pytest.fixture
# def app(tmp_path):
#     # 1) create a fresh instance folder & DB file
#     instance = tmp_path / "instance"
#     instance.mkdir()
#     db_file = tmp_path / "test.sqlite"

#     # 2) build the app
#     app = create_app()
#     app.config.update({
#         "TESTING":    True,
#         "DATABASE":   str(db_file),
#         "SECRET_KEY": "test",
#     })
#     app.instance_path = str(instance)

#     # 3) override open_resource so seed.sql is a no-op
#     real_open = app.open_resource
#     def fake_open(path, mode='rb'):
#         if path.endswith("seed.sql"):
#             # skip seed data entirely in tests
#             return io.BytesIO(b"")
#         return real_open(path, mode)
#     app.open_resource = fake_open

#     # 4) initialize schema only (seed.sql is stubbed)
#     with app.app_context():
#         init_db()

#         # 5) load our own tests/data.sql fixtures
#         db = get_db()
#         data_sql = os.path.join(os.getcwd(), "tests", "data.sql")
#         with open(data_sql, "rb") as f:
#             db.executescript(f.read().decode("utf8"))

#     yield app

# @pytest.fixture
# def client(app):
#     return app.test_client()

# @pytest.fixture
# def runner(app):
#     return app.test_cli_runner()

# tests/conftest.py

# import os
# import io
# import sys
# import sqlite3
# import pytest
# from flask import Flask
# from flask.testing import FlaskClient, FlaskCliRunner
# from flaskr import create_app
# from flaskr.db import get_db, init_db
# from typing import Generator

# # allow top-level imports
# sys.path.insert(0, os.getcwd())

# @pytest.fixture
# def app(tmp_path) -> Generator[Flask, None, None]:
#     # 1) create a fresh instance folder & DB file
#     instance = tmp_path / "instance"
#     instance.mkdir()
#     db_file = tmp_path / "test.sqlite"

#     # 2) build the app
#     app = create_app()
#     app.config.update({
#         "TESTING":    True,
#         "DATABASE":   str(db_file),
#         "SECRET_KEY": "test",
#     })
#     app.instance_path = str(instance)

#     # 3) override open_resource so seed.sql is a no-op
#     real_open = app.open_resource
#     def fake_open(path: str, mode: str = 'rb') -> io.BytesIO:
#         if path.endswith("seed.sql"):
#             # skip seed data entirely in tests
#             return io.BytesIO(b"")
#         return real_open(path, mode)
#     app.open_resource = fake_open

#     # 4) initialize schema only (seed.sql is stubbed)
#     with app.app_context():
#         init_db()

#         # 5) load our own tests/data.sql fixtures
#         db = get_db()
#         data_sql = os.path.join(os.getcwd(), "tests", "data.sql")
#         with open(data_sql, "rb") as f:
#             db.executescript(f.read().decode("utf8"))

#     yield app

# @pytest.fixture
# def client(app: Flask) -> FlaskClient:
#     return app.test_client()

# @pytest.fixture
# def runner(app: Flask) -> FlaskCliRunner:
#     return app.test_cli_runner()


import os
import io
import sys
import sqlite3
import pytest
from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner
from flaskr import create_app
from flaskr.db import get_db, init_db
from typing import Generator, Any, cast, IO

# allow top-level imports
sys.path.insert(0, os.getcwd())

@pytest.fixture
def app(tmp_path) -> Generator[Flask, None, None]:
    instance = tmp_path / "instance"
    instance.mkdir()
    db_file = tmp_path / "test.sqlite"

    app = create_app()
    app.config.update({
        "TESTING":    True,
        "DATABASE":   str(db_file),
        "SECRET_KEY": "test",
    })
    app.instance_path = str(instance)

    real_open = app.open_resource

    def fake_open(path: str, mode: str = 'rb') -> IO[bytes]: 
        if path.endswith("seed.sql"):
            return io.BytesIO(b"")
        return real_open(path, mode)

    setattr(app, "open_resource", cast(Any, fake_open))  

    with app.app_context():
        init_db()
        db = get_db()
        data_sql = os.path.join(os.getcwd(), "tests", "data.sql")
        with open(data_sql, "rb") as f:
            db.executescript(f.read().decode("utf8"))

    yield app

@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()

@pytest.fixture
def runner(app: Flask) -> FlaskCliRunner:
    return app.test_cli_runner()
