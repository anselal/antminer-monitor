# if set to 1 the app will not load .flaskenv and .env
FLASK_SKIP_DOTENV=0

# DO NOT CHANGE THIS
FLASK_APP="antminermonitor/app.py:create_app()"

# default '127.0.0.1'. '0.0.0.0' gives access from anywhere
FLASK_RUN_HOST="0.0.0.0"

# you can change this to whatever you want
FLASK_RUN_PORT=5000

# default 'production'
FLASK_ENV="development"
