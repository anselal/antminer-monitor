from app.models import MinerModel, Settings
from app import db
from sqlalchemy.exc import IntegrityError
from app.views import ModelType

db.create_all()
models = []
# TODO: Find a better place to put this hashrate thingy
models.append(MinerModel(model=ModelType.L3Plus, chips='72,72,72,72', temp_keys='temp2_', description='Litecoin Miner 504 MH/s', hashrate_value=504, hashrate_unit='MH/s', hashrate_unit_in_api='MH/s', high_temp=70, max_fan_rpm=7125, watts=800))
models.append(MinerModel(model=ModelType.S9, chips='63,63,63', temp_keys='temp2_', description='Bitcoin Miner 13.5 TH/s', hashrate_value=13.5, hashrate_unit='TH/s', hashrate_unit_in_api='GH/s', high_temp=80, max_fan_rpm=7125, watts=1323))
models.append(MinerModel(model=ModelType.D3, chips='60,60,60', temp_keys='temp2_', description='DASH Miner 17 GH/s', hashrate_value=17, hashrate_unit='GH/s', hashrate_unit_in_api='MH/s', high_temp=80, max_fan_rpm=7125, watts=1200))
models.append(MinerModel(model=ModelType.Avalon741, chips='88', temp_keys='', description='Avalon 741 - 7 TH/s', hashrate_value=7, hashrate_unit='TH/s', hashrate_unit_in_api='GH/s', high_temp=90, max_fan_rpm=0, watts=1150))
models.append(MinerModel(model=ModelType.Avalon821, chips='104', temp_keys='', description='Avalon 821 - 11 TH/s', hashrate_value=10, hashrate_unit='TH/s', hashrate_unit_in_api='GH/s', high_temp=90, max_fan_rpm=0, watts=1200))
models.append(MinerModel(model=ModelType.GekkoScience, chips='1', temp_keys='', description='GekkoScience 2PAC Rev2 BM1384', hashrate_value=15, hashrate_unit='GH/s', hashrate_unit_in_api='MH/s', high_temp=0, max_fan_rpm=0, watts=5))
models.append(MinerModel(model=ModelType.AntRouterR1LTC, chips='1', temp_keys='', description='L1-RTC Router', hashrate_value=1.29, hashrate_unit="MH/s", hashrate_unit_in_api='MH/s', high_temp=0, max_fan_rpm=0, watts=4))

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


