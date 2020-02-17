from flask_login.mixins import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy import Column, Integer, VARCHAR
from antminermonitor.database import Base


class User(UserMixin, Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(VARCHAR(64), index=True, unique=True)
    email = Column(VARCHAR(120), index=True, unique=True)
    password_hash = Column(VARCHAR(128))
    surname = Column(VARCHAR(100))
    firstname = Column(VARCHAR(100))
    active = Column(Integer, default=1)

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
