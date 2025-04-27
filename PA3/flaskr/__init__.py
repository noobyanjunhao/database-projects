import os
from flask import Flask
from .db import get_db
from datetime import datetime
import pandas as pd
from . import db

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite')
    )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)

    from flaskr.views.main import main_bp
    from flaskr.views.bill import bill_bp
    from flaskr.views.unit import unit_bp
    from flaskr.views.export import export_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(bill_bp)
    app.register_blueprint(unit_bp)
    app.register_blueprint(export_bp)

    # on first run, initialize the database; we don’t cover this in tests
    if not os.path.exists(app.config['DATABASE']):  # pragma: no cover
        with app.app_context():
            db.init_db()  # pragma: no cover

    return app
