from flask_login.mixins import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from antminermonitor.extensions import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.VARCHAR(64), index=True, unique=True)
    email = db.Column(db.VARCHAR(120), index=True, unique=True)
    password_hash = db.Column(db.VARCHAR(128))
    surname = db.Column(db.VARCHAR(100))
    firstname = db.Column(db.VARCHAR(100))
    active = db.Column(db.Integer, default=1)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'firstname': self.firstname,
            'surname': self.surname,
            'email': self.email
        }

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
