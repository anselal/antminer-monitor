from antminermonitor.extensions import db


class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))

    def __repr__(self):
        return "Settings(name='{}', value={}, description='{}')" \
            .format(self.name, self.value, self.description)
