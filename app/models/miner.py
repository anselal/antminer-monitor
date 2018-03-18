from app import db
from app.models.miner_event import MinerEvent

class Miner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(15), unique=True, nullable=False)
    model_id = db.Column(db.Integer, db.ForeignKey('miner_model.id'), nullable=False)
    model = db.relationship("MinerModel", backref="miners")
    remarks = db.Column(db.String(255), nullable=True)
    # TODO: There is no current way of setting this through the interface
    count = db.Column(db.Integer, nullable=False)
    miner_event = db.relationship('MinerEvent', backref='miner', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return "Miner(ip='{}', model='{}', remarks='{}')".format(self.ip, self.model, self.remarks)
