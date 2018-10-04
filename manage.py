import subprocess

from flask.cli import FlaskGroup

from antminermonitor.app import create_app
from antminermonitor.blueprints.asicminer.models.miner import Miner
from antminermonitor.blueprints.asicminer.models.miner_model import MinerModel
from antminermonitor.blueprints.asicminer.models.settings import Settings
from antminermonitor.blueprints.user.models import User
from antminermonitor.extensions import db

cli = FlaskGroup(create_app=create_app)


@cli.command()
def create_db():
    """
        Create database. Add miner models and settings.
    """
    from sqlalchemy.exc import IntegrityError

    db.create_all()
    models = []
    models.append(
        MinerModel(
            model='L3+',
            chips='72,72,72,72',
            temp_keys='temp2_',
            description='Litecoin Miner 504 MH/s'))
    models.append(
        MinerModel(
            model='S7',
            chips='45,45,45',
            temp_keys='temp',
            description='Bitcoin Miner 4.5 TH/s'))
    models.append(
        MinerModel(
            model='S9',
            chips='63,63,63',
            temp_keys='temp2_',
            description='Bitcoin Miner 13.5 TH/s'))
    models.append(
        MinerModel(
            model='D3',
            chips='60,60,60',
            temp_keys='temp2_',
            description='DASH Miner 17 GH/s'))
    models.append(
        MinerModel(
            model='T9',
            chips='57,57,57',
            temp_keys='temp2_',
            description='Bitcoin Miner 12.5 TH/s'))
    models.append(
        MinerModel(
            model='T9+',
            chips='54,54,54',
            temp_keys='temp2_',
            description='Bitcoin Miner 10.5 TH/s'))
    models.append(
        MinerModel(
            model='A3',
            chips='60,60,60',
            temp_keys='temp2_',
            description='Siacoin Miner 815 GH/s'))
    models.append(
        MinerModel(
            model='L3',
            chips='36,36,36,36',
            temp_keys='temp2_',
            description='Litecoin Miner 250 MH/s'))
    models.append(
        MinerModel(
            model='R4',
            chips='63,63',
            temp_keys='temp2_',
            description='Bitcoin Miner 8 TH/s'))
    models.append(
        MinerModel(
            model='V9',
            chips='45,45,45',
            temp_keys='temp2_',
            description='Bitcoin Miner 4 TH/s'))
    models.append(
        MinerModel(
            model='X3',
            chips='60,60,60',
            temp_keys='temp2_',
            description='CryptoNight Miner 220 KH/s'))
    models.append(
        MinerModel(
            model='Z9 mini',
            chips='4,4,4',
            temp_keys='temp2_',
            description='Equihash Miner 10 KSol/s'))
    models.append(
        MinerModel(
            model='E3',
            chips='2,2,2,2,2,2,2,2,2',
            temp_keys='temp2_',
            description='Ethash Miner 190 MH/s'))
    settings = []
    settings.append(
        Settings(name="temperature_alert", value="80", description=""))
    settings.append(
        Settings(
            name="email_alert",
            value="True",
            description="Whether to send an email on alert"))

    try:
        for model in models:
            db.session.add(model)
            db.session.commit()

        for setting in settings:
            db.session.add(setting)
            db.session.commit()
    except IntegrityError:
        print("[INFO] Database already exists.")
    else:
        print("[INFO] Database successfully created.")


@cli.command()
def update_db():
    """
        Update miner models and settings.
    """
    print("[INFO] Starting DB update...")
    # backup Miner data
    miners = []
    backup = Miner.query.all()

    print("[INFO] Backing up miners...")
    for miner in backup:
        miners.append(
            Miner(
                ip=str(miner.ip),
                model_id=int(miner.model.id),
                remarks=str(miner.remarks)))

    # drop all tables
    print("[INFO] Dropping tables...")
    Miner.__table__.drop(db.engine)
    MinerModel.__table__.drop(db.engine)
    Settings.__table__.drop(db.engine)
    # create all tables
    print("[INFO] Recreating all tables...")
    db.create_all()

    # add supported MinerModels
    models = []
    models.append(
        MinerModel(
            model='L3+',
            chips='72,72,72,72',
            temp_keys='temp2_',
            description='Litecoin Miner 504 MH/s'))
    models.append(
        MinerModel(
            model='S7',
            chips='45,45,45',
            temp_keys='temp',
            description='Bitcoin Miner 4.5 TH/s'))
    models.append(
        MinerModel(
            model='S9',
            chips='63,63,63',
            temp_keys='temp2_',
            description='Bitcoin Miner 13.5 TH/s'))
    models.append(
        MinerModel(
            model='D3',
            chips='60,60,60',
            temp_keys='temp2_',
            description='DASH Miner 17 GH/s'))
    models.append(
        MinerModel(
            model='T9',
            chips='57,57,57',
            temp_keys='temp2_',
            description='Bitcoin Miner 12.5 TH/s'))
    models.append(
        MinerModel(
            model='T9+',
            chips='54,54,54',
            temp_keys='temp2_',
            description='Bitcoin Miner 10.5 TH/s'))
    models.append(
        MinerModel(
            model='A3',
            chips='60,60,60',
            temp_keys='temp2_',
            description='Siacoin Miner 815 GH/s'))
    models.append(
        MinerModel(
            model='L3',
            chips='36,36,36,36',
            temp_keys='temp2_',
            description='Litecoin Miner 250 MH/s'))
    models.append(
        MinerModel(
            model='R4',
            chips='63,63',
            temp_keys='temp2_',
            description='Bitcoin Miner 8 TH/s'))
    models.append(
        MinerModel(
            model='V9',
            chips='45,45,45',
            temp_keys='temp2_',
            description='Bitcoin Miner 4 TH/s'))
    models.append(
        MinerModel(
            model='X3',
            chips='60,60,60',
            temp_keys='temp2_',
            description='CryptoNight Miner 220 KH/s'))
    models.append(
        MinerModel(
            model='Z9 mini',
            chips='4,4,4',
            temp_keys='temp2_',
            description='Equihash Miner 10 KSol/s'))
    models.append(
        MinerModel(
            model='E3',
            chips='2,2,2,2,2,2,2,2,2',
            temp_keys='temp2_',
            description='Ethash Miner 190 MH/s'))

    # add Settings
    settings = []
    settings.append(
        Settings(name="temperature_alert", value="80", description=""))
    settings.append(
        Settings(
            name="email_alert",
            value="True",
            description="Whether to send an email on alert"))

    # commit MinerModels to database
    print("[INFO] Adding models...")
    for model in models:
        db.session.add(model)
        db.session.commit()
    # commit Settings to database
    print("[INFO] Adding settings...")
    for setting in settings:
        db.session.add(setting)
        db.session.commit()
    # commit backed up Miners to database
    print("[INFO] Adding backed up miners...")
    for miner in miners:
        db.session.add(miner)
        db.session.commit()

    print("[INFO] Updating DB successfully finished")


@cli.command()
def create_admin():
    """
        Create admin user if not exist with default password 'antminermonitor'
    """
    db.create_all()
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
        db.session.add(admin)
        db.session.commit()
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
