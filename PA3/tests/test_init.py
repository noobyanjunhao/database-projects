import os
import pytest
from flaskr import create_app
from flaskr.db import init_db

def test_create_app_defaults(app):
    assert app.config['TESTING']
    assert app.config['SECRET_KEY'] == 'test'
    assert os.path.exists(app.config['DATABASE'])

def test_init_db_command(runner):
    result = runner.invoke(args=['init-db'])
    assert result.exit_code == 0
    assert 'Initialized the database.' in result.output
