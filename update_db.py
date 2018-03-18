from app.models import Miner, MinerModel, Settings
from app import db

print("[INFO] Starting DB update...")
# backup Miner data
miners = []
backup = Miner.query.all()

print("[INFO] Backing up miners...")
for miner in backup:
    miners.append(Miner(ip=str(miner.ip), model_id=int(miner.model.id), remarks=str(miner.remarks)))

# drop all tables
print("[INFO] Dropping tables...")
db.drop_all()
# create all tables
print("[INFO] Recreating all tables...")
db.create_all()

# add supported MinerModels
models = []
models.append(MinerModel(model='L3+', chips='72,72,72,72', temp_keys='temp2_', description='Litecoin Miner 504 MH/s'))
models.append(MinerModel(model='S7', chips='45,45,45', temp_keys='temp', description='Bitcoin Miner 4.5 TH/s'))
models.append(MinerModel(model='S9', chips='63,63,63', temp_keys='temp2_', description='Bitcoin Miner 13.5 TH/s'))
models.append(MinerModel(model='D3', chips='60,60,60', temp_keys='temp2_', description='DASH Miner 17 GH/s'))
models.append(MinerModel(model='T9', chips='57,57,57', temp_keys='temp2_', description='Bitcoin Miner 12.5 TH/s'))
models.append(MinerModel(model='A3', chips='60,60,60', temp_keys='temp2_', description='Siacoin Miner 815 GH/s'))
models.append(MinerModel(model='L3', chips='36,36,36,36', temp_keys='temp2_', description='Litecoin Miner 250 MH/s'))
# add Settings
settings = []
settings.append(Settings(name="temperature_alert", value="80", description=""))
settings.append(Settings(name="email_alert", value="True", description="Whether to send an email on alert"))


# commit MinerModels to database
print("[INFO] Adding models...")
for model in models:
    db.session.add(model)
    db.session.commit()
#commit Settings to database
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