from app import db


class MinerModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(15), unique=True, nullable=False)
    chips = db.Column(db.String(24), nullable=False)
    temp_keys = db.Column(db.String(5), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    hashrate_value = db.Column(db.Float, nullable=False)
    hashrate_unit = db.Column(db.String(10), nullable=False)
    high_temp = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return "MinerModel(model='{}', chips={}, description='{}')".format(self.model, self.chips, self.description)
