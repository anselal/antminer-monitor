from app import db
from datetime import datetime

class MinerEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    miner_id = db.Column(db.Integer, db.ForeignKey('miner.id'),
        nullable=False)
    event_type = db.Column(db.String(10), nullable=False)
    message = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now())

    def __repr__(self):
        return "MinerModel(model='{}', chips={}, description='{}')".format(self.model, self.chips, self.description)
