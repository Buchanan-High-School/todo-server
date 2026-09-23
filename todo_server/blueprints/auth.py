from flask import abort, Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from werkzeug.utils import secure_filename

from todo_server.extensions import db
from todo_server.models import User

bp = Blueprint("auth", __name__)


@bp.get("/register")
def get_register_form():
    return render_template("register.html")


@bp.post("/register")
def register():
    form = request.form

    if form["password"] != form["password_again"]:
        flash("Your passwords do not match")
        return redrect(url_for("auth.get_register_form"))

    user = User(
        email=form["email"], first_name=form["first_name"], last_name=form["last_name"]
    )

    user.set_password(form["password"])
    db.session.add(user)
    db.session.commit()
    login_user(user)

    return redirect("/")


@bp.get("/login")
def get_login():
    return render_template("login.html")


@bp.post("/login")
def login():
    form = request.form

    user = User.query.filter(User.email == form["email"]).first()
    if user is None or not user.check_password(form["password"]):
        abort(401)

    login_user(user)

    return redirect(url_for("deploy.upload"))


@bp.get("/logout")
def logout():
    logout_user()
    return redirect("/")
