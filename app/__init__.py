from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
import logging
import os

__version__ = "v0.2.0"
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'super secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db/app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

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

def remove_leading_slash(path):
  if path.startswith("/"):
    return path[1:]
  else:
    return path
def url_for_ex(endpoint, **values):
    # Remove the leading slashes because its required if
    # this is hosted behind a nginx server.
    return remove_leading_slash(url_for(endpoint, **values))
app.jinja_env.globals.update(url_for_ex=url_for_ex)

# Global variable for agent
last_status_is_ok = True
last_run_time = 0

from app.views import antminer, antminer_json
