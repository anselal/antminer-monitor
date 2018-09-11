import os

__VERSION__ = '0.4.0'

DEBUG = True
LOG_LEVEL = 'DEBUG'  # CRITICAL / ERROR / WARNING / INFO / DEBUG

SECRET_KEY = 'super secret key'

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))

# SQLAlchemy
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + \
    os.path.join(basedir, 'antminermonitor/db/app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
