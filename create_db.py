from app.models import MinerModel, Settings
from app import db
from sqlalchemy.exc import IntegrityError

db.create_all()
models = []
models.append(MinerModel(model='L3+', chips='72,72,72,72', temp_keys='temp2_', description='Litecoin Miner 504 MH/s'))
models.append(MinerModel(model='S7', chips='45,45,45', temp_keys='temp', description='Bitcoin Miner 4.5 TH/s'))
models.append(MinerModel(model='S9', chips='63,63,63', temp_keys='temp2_', description='Bitcoin Miner 13.5 TH/s'))
models.append(MinerModel(model='D3', chips='60,60,60', temp_keys='temp2_', description='DASH Miner 17 GH/s'))
models.append(MinerModel(model='T9', chips='57,57,57', temp_keys='temp2_', description='Bitcoin Miner 12.5 TH/s'))
models.append(MinerModel(model='A3', chips='60,60,60', temp_keys='temp2_', description='Siacoin Miner 815 GH/s'))
models.append(MinerModel(model='L3', chips='36,36,36,36', temp_keys='temp2_', description='Litecoin Miner 250 MH/s'))
models.append(MinerModel(model='R4', chips='63,63', temp_keys='temp2_', description='Bitcoin Miner 8 TH/s'))
models.append(MinerModel(model='V9', chips='45,45,45', temp_keys='temp2_', description='Bitcoin Miner 4 TH/s'))
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
    print("[INFO] Database already exists.")
else:
    print("[INFO] Database successfully created.")

