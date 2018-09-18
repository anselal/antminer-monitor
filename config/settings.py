import os
from dotenv import load_dotenv


basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
load_dotenv(os.path.join(basedir, '.env'))

__VERSION__ = '0.4.0'

DEBUG = True
LOG_LEVEL = 'DEBUG'  # CRITICAL / ERROR / WARNING / INFO / DEBUG

SECRET_KEY = os.environ.get('SECRET_KEY') or 'super secret key'

# SQLAlchemy
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + \
    os.path.join(basedir, 'antminermonitor/db/app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
