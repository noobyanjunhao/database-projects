import os
from flask import Flask
from .db import get_db
from datetime import datetime
import pandas as pd  # type: ignore
from . import db
from typing import Optional, Dict, Any, cast

def create_app(test_config: Optional[Dict[str, Any]] = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(  # type: ignore
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite')
    )
    
    if test_config is not None:
        app.config.update(test_config)

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

    # on first run, initialize the database; we don't cover this in tests
    if not os.path.exists(app.config['DATABASE']):  # type: ignore # pragma: no cover
        with app.app_context():
            db.init_db()  # pragma: no cover

    return app
