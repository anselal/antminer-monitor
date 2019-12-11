from antminermonitor.extensions import db


class Miner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(15), unique=True, nullable=False)
    model_id = db.Column(db.String(15), nullable=False)
    remarks = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return "Miner(ip='{}', model_id='{}', remarks='{}')" \
            .format(self.ip, self.model_id, self.remarks)
