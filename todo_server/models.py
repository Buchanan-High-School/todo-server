import uuid
from dataclasses import dataclass
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


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(32))
    description = db.Column(db.String(256))
    due = db.Column(db.Date, nullable=False, default=default_due)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.String(32))
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
    last_name = db.Column(db.String(32), nullable=False)
    first_name = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(32), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    api_id = db.Column(db.String(32))

    projects = db.relationship(
        "Project",
        backref=backref("user", single_parent=True),
        lazy="dynamic",
        passive_deletes=True,
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        db.session.commit()

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    owner = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_on = db.Column(db.Date, default=func.now())
