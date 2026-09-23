import os
import zipfile

from flask import abort, Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from werkzeug.utils import secure_filename

from todo_server.extensions import db

bp = Blueprint("deploy", __name__)

UPLOAD_FOLDER = os.path.dirname(os.path.realpath(__file__))
ALLOWED_EXTENSIONS = set(["zip"])

# Init a db connection to  the glitchlet database


# Get the upload form
@bp.get("/upload")
def upload():
    if current_user.is_anonymous:
        return redirect(url_for("auth.login"))
    # Get the upload form, templates/upload.html
    return render_template("upload.html")
    pass


# Handle the upload
@bp.post("/upload")
def handle_upload():
    # get the user id

    if "file" not in request.files:
        flash("No file sent")
        return redirect(request.url)

    file = request.files["file"]
    if file.filename == "":
        flash("No file selected")
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        zip_ref = zipfile.ZipFile(os.path.join(UPLOAD_FOLDER, filename), "r")
        zip_ref.extractall(UPLOAD_FOLDER)
        zip_ref.close()
        return redirect(url_for("upload_file", filename=filename))
