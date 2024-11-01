from flask import Flask

from app.api import config_blueprint
from config import Config
from app.extension import config_extensions


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    config_extensions(app)
    config_blueprint(app)
    return app

