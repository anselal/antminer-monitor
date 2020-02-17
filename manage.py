import subprocess

from flask.cli import FlaskGroup

from antminermonitor.app import create_app
from antminermonitor.blueprints.asicminer.models.miner import Miner
from antminermonitor.blueprints.asicminer.models.settings import Settings
from antminermonitor.blueprints.user.models import User
from antminermonitor.database import db_session, init_db

cli = FlaskGroup(create_app=create_app)


@cli.command()
def create_db():
    """
        Create database. Add miner models and settings.
    """
    from sqlalchemy.exc import IntegrityError

    init_db()

    settings = []
    settings.append(
        Settings(name="temperature_alert", value="80", description=""))
    settings.append(
        Settings(
            name="email_alert",
            value="True",
            description="Whether to send an email on alert"))

    try:
         for setting in settings:
            db_session.add(setting)
            db_session.commit()
    except IntegrityError:
        print("[INFO] Database already exists.")
    else:
        print("[INFO] Database successfully created.")


@cli.command()
def create_admin():
    """
        Create admin user if not exist with default password 'antminermonitor'
    """
    init_db()
    print("[INFO] Checking if admin user exists...")
    admin = User.query.filter_by(username='admin').first()

    if not admin:
        print("[INFO] Creating admin user with password 'antminermonitor'...")
        admin = User(
            username='admin',
            email='foo@bar.org',
            surname='admin',
            firstname='admin',
            active=0)
        admin.set_password('antminermonitor')
        db_session.add(admin)
        db_session.commit()
    elif admin:
        print("[INFO] Admin user already exists.")
    else:
        print("[INFO] Something went wrong.")


@cli.command()
def format():
    """Runs the yapf and isort formatters over the project."""
    isort = 'isort -rc *.py antminermonitor/'
    yapf = 'yapf -r -i *.py antminermonitor/'

    print('Running {}'.format(isort))
    subprocess.call(isort, shell=True)

    print('Running {}'.format(yapf))
    subprocess.call(yapf, shell=True)


if __name__ == "__main__":
    cli()
