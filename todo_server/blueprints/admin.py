from flask import abort, Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from todo_server.extensions import db
from todo_server.models import Project, User

bp = Blueprint("admin", __name__)


@bp.get("/admin/projects")
def admin_index():
    page = request.args.get("page", 1, type=int)
    if current_user.usertype_id == 2:
        stmt = (
            db.select(Project)
            .where(Project.owner == current_user.id)
            .order_by(Project.created_on.desc())
        )
    else:
        stmt = db.select(Project).order_by(Project.created_on.desc())
    pagination = db.paginate(stmt, page=page, per_page=25)
    return render_template(
        "admin_index.html", items=pagination.items, pagination=pagination
    )


@bp.get("/admin/users")
def user_admin():
    if current_user.usertype_id != 1:
        flash("You are not authorized to view this page.")
        return redirect(url_for("index")), 401

    stmt = db.select(User).order_by(User.last_name)
    users = db.session.scalars(stmt).all()

    return render_template("admin_users.html", users=users)
