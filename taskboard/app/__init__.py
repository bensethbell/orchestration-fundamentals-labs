from flask import Flask

from app.db import init_db


def create_app(config_overrides=None):
    app = Flask(__name__)
    app.config["DATABASE_PATH"] = "taskboard.db"
    app.config["SECRET_KEY"] = "dev-only-not-for-production"

    if config_overrides:
        app.config.update(config_overrides)

    init_db(app)

    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app
