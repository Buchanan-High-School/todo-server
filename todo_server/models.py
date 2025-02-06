import uuid
from datetime import timedelta, date

from flask_login import UserMixin
from sqlalchemy.orm import backref
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash


from todo_server.extensions import db, login_manager


def default_due():
    valid = date.today() + timedelta(days=1)
    return valid


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(80))
    device_key = db.Column(db.String(80))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", back_populates="devices")

    def __init__(self, device_name, user_id, device_key=None):
        self.device_name = device_name
        self.user_id = user_id
        self.device_key = device_key or uuid.uuid4().hex

    def json(self):
        return {
            "device_name": self.device_name,
            "device_key": self.device.key,
            "user_id": self.user_id,
        }

    @classmethod
    def find_by_name(cls, device_name):
        return cls.query.filter_by(device_name=device_name).first()

    @classmethod
    def find_by_device_key(cls, device_key):
        return cls.query.filter_by(device_key=device_key).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    due = db.Column(db.Date, nullable=False, default=default_due)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer)
    completed = db.Column(db.Boolean, default=False)

    def update(self, data):
        for key, value in data.items():
            if key == "courses":
                continue
            else:
                setattr(self, key, value)
        db.session.commit()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=True)
    email = db.Column(db.String(32), unique=True)
    devices = db.relationship("Device", back_populates="user")
