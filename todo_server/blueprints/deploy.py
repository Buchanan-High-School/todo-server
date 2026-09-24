import os
import zipfile

from flask import (
    abort,
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_login import current_user, login_user, logout_user
from markupsafe import Markup
from werkzeug.utils import secure_filename

from todo_server.extensions import db
from todo_server.models import Project

bp = Blueprint("deploy", __name__)

ALLOWED_EXTENSIONS = set(["zip"])


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_user_dir(user):
    path_exists = os.path.isdir(
        os.path.join(current_app.config["UPLOAD_PATH"], user.last_name.lower())
    )

    if not path_exists:
        os.mkdir(
            os.path.join(current_app.config["UPLOAD_PATH"], user.last_name.lower())
        )

    dir = os.path.join(current_app.config["UPLOAD_PATH"], user.last_name.lower())

    return dir


# Get the upload form
@bp.get("/upload")
def upload():
    if current_user.is_anonymous:
        flash("You need to log in first.")
        return redirect(url_for("auth.login"))
    # Get the upload form, templates/upload.html
    return render_template("upload.html")
    pass


# Handle the upload
@bp.post("/upload")
def handle_upload():

    # breakpoint()

    if "file" not in request.files:
        flash("No file sent")
        return redirect(request.url)

    file = request.files["file"]
    if file.filename == "":
        flash("No file selected")
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename).split(".")[0]

        # Check that the user's directory exists.
        user_dir = get_user_dir(current_user)

        project_path = os.path.join(user_dir, request.form["name"])

        if os.path.isdir(project_path):
            flash(
                "A project with that name already exists. Use a different project name."
            )
            return render_template("upload.html"), 409

        # make the new directory for the project based on the filename
        os.mkdir(project_path)

        # save the zipfile and then extract immediately.
        file.save(os.path.join(project_path, filename))
        zip_ref = zipfile.ZipFile(os.path.join(project_path, filename), "r")
        zip_ref.extractall(project_path)
        zip_ref.close()
        # Get the published URL for the file
        live_url = url_for(
            "deploy.open_single_project",
            last_name=current_user.last_name.lower(),
            project_name=request.form["name"],
        )

        # Finally, save it to the database against the current user
        project = Project(
            name=request.form["name"],
            owner=current_user.id,
        )

        db.session.add(project)
        db.session.commit()

        message = Markup(
            "View your project at <a href='{}' target='_blank'>{}</a>".format(
                live_url, live_url
            )
        )
        flash(message)
        return redirect(url_for("deploy.upload"))


@bp.get("/user/<string:last_name>/<string:project_name>")
def open_single_project(last_name, project_name):
    return send_from_directory(
        "user/{}/{}".format(last_name, project_name), "index.html"
    )


@bp.get("/projects")
def get_projects():
    # Get all deployed projects for quick management
    pass
