from flask import Flask

from antminermonitor.blueprints.asicminer import antminer, antminer_json
from antminermonitor.blueprints.user import user
from antminermonitor.extensions import login_manager, migrate
from antminermonitor.blueprints.asicminer.models.miner import Miner
from antminermonitor.blueprints.asicminer.models.settings import Settings
from antminermonitor.blueprints.user.models import User
from antminermonitor.database import db_session, init_db

import logging
import os


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
    app.register_blueprint(user, url_prefix='/user')
    authentication(app, User)
    extensions(app)

    @app.shell_context_processor
    def make_shell_context():
        return dict(app=app, db=db, Miner=Miner, Settings=Settings, User=User)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

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
    login_manager.init_app(app)
    migrate.init_app(app, db_session)

    return


def authentication(app, user_model):
    """
    Initialize the Flask-Login extension (mutates the app passed in).

    :param app: Flask application instance
    :param user_model: Model that contains the authentication information
    :type user_model: SQLAlchemy model
    :return: None
    """
    login_manager.login_view = 'user.login'
    # login_manager.login_message = ''
    login_manager.refresh_view = 'user.login'
    login_manager.needs_refresh_message = 'You need to login again to access'
    ' this page!!!'

    @login_manager.user_loader
    def load_user(uid):
        return user_model.query.get(uid)
