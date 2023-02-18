import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
load_dotenv(os.path.join(basedir, '.env'))

import json

with open("config/models.json", "r") as json_data:
    models = json.load(json_data)

MODELS = models

import multiprocessing as m

NUM_THREADS = m.cpu_count() - 1 or 1

__VERSION__ = '0.5.0'

DEBUG = True
LOG_LEVEL = 'DEBUG'  # CRITICAL / ERROR / WARNING / INFO / DEBUG

SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(64)

# SQLAlchemy
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + \
    os.path.join(basedir, 'antminermonitor/db/app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Session
#USE_SESSION_FOR_NEXT = True

# Mail
MAIL_SERVER = os.environ.get('MAIL_SERVER')
MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

# TELEGRAM
TELEGRAM_BOT_TOKEN = ""
TELEGRAM_CHAT_ID = ""
