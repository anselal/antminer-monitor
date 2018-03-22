from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager, Server
from flask_migrate import Migrate

import logging
import os

__version__ = "v0.4.0"
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config.settings')
app.config.from_pyfile('settings.py', silent=True)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
server = Server(host='0.0.0.0', port=5000)
manager.add_command('runserver', server)

gunicorn_error_logger = logging.getLogger('gunicorn.error')
app.logger.handlers.extend(gunicorn_error_logger.handlers)
app.logger.setLevel(logging.DEBUG)

# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

# create a file handler
handler = logging.FileHandler(os.path.join(basedir, 'logs/antminer_monitor.log'), mode='a')  # mode 'a' is default
handler.setLevel(logging.WARNING)

# create a logging format
formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
handler.setFormatter(formatter)

# add handlers to the logger
logger.addHandler(handler)

from app.views import antminer, antminer_json
