from app.models import MinerModel, Settings
from app import db
from sqlalchemy.exc import IntegrityError

db.create_all()
models = []
models.append(MinerModel(model='L3+', chips='72,72,72,72', temp_keys='temp2_', description='Litecoin Miner 504 MH/s'))
models.append(MinerModel(model='S7', chips='45,45,45', temp_keys='temp', description='Bitcoin Miner 4.5 TH/s'))
models.append(MinerModel(model='S9', chips='63,63,63', temp_keys='temp2_', description='Bitcoin Miner 13.5 TH/s'))
models.append(MinerModel(model='D3', chips='60,60,60', temp_keys='temp2_', description='DASH Miner 17 GH/s'))
models.append(MinerModel(model='A3', chips='60,60,60', temp_keys='temp2_', description='Siacoin (Blake2b) Miner 815 GH/s'))
settings = []
settings.append(Settings(name="temperature_alert", value="80", description=""))
settings.append(Settings(name="email_alert", value="True", description="Whether to send an email on alert"))

try:
    for model in models:
        db.session.add(model)
        db.session.commit()

    for setting in settings:
        db.session.add(setting)
        db.session.commit()
except IntegrityError:
    print("Database already exists.")
else:
    print("Database successfully created.")

