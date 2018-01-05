from app import db


class Miner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    local_ip = db.Column(db.String(15), unique=True, nullable=False)
    remote_hostport = db.Column(db.String(255), unique=True, nullable=False)
    model_id = db.Column(db.Integer, db.ForeignKey('miner_model.id'), nullable=False)
    model = db.relationship("MinerModel", backref="miners")
    remarks = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return "Miner(local_ip='{}', remote_hostport='{}', model='{}', remarks='{}')".format(self.local_ip, self.remote_hostport, self.model, self.remarks)
