import os
from flask import Flask

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

    from . import db
    db.init_app(app)

    if not os.path.exists(app.config['DATABASE']):
        with app.app_context():
            db.init_db()

    # from . import auth, billing
    # app.register_blueprint(auth.bp)
    # app.register_blueprint(billing.bp)

    return app
