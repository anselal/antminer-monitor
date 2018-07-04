from flask import Flask

from antminermonitor.blueprints.asicminer import antminer, antminer_json
from antminermonitor.extensions import (
    db,
    migrate,
)
from antminermonitor.blueprints.asicminer.models.miner import Miner
from antminermonitor.blueprints.asicminer.models.miner_model import MinerModel
from antminermonitor.blueprints.asicminer.models.settings import Settings

import logging
import os


__version__ = "v0.4.0"
basedir = os.path.abspath(os.path.dirname(__file__))


def create_app(script_info=None, settings_override=None):
    """
    Create a Flask application using the app factory pattern.

    :return: Flask app
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config.settings')
    app.config.from_pyfile('settings.py', silent=True)

    if settings_override:
        app.config.update(settings_override)

    app.register_blueprint(antminer)
    app.register_blueprint(antminer_json)
    extensions(app)

    @app.shell_context_processor
    def make_shell_context():
        return dict(app=app, db=db, Miner=Miner, MinerModel=MinerModel,
                    Settings=Settings)

    return app


def create_logger(app=None):
    """

    """
    app = app or create_app()
    gunicorn_error_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers.extend(gunicorn_error_logger.handlers)
    app.logger.setLevel(app.config['LOG_LEVEL'])

    # logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.WARNING)

    # create a file handler
    handler = logging.FileHandler(os.path.join(
        basedir, 'logs/antminer_monitor.log'), mode='a')  # mode 'a' is default
    handler.setLevel(logging.WARNING)

    # create a logging format
    formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s')
    handler.setFormatter(formatter)

    # add handlers to the logger
    logger.addHandler(handler)

    return logger


def extensions(app):
    """
    Register 0 or more extensions (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    db.init_app(app)
    migrate.init_app(app, db)

    return
