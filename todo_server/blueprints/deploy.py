import os
import zipfile

from flask import abort, Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from werkzeug.utils import secure_filename

from todo_server.extensions import db

bp = Blueprint("deploy", __name__)

UPLOAD_FOLDER = os.path.dirname(os.path.realpath(__file__))
ALLOWED_EXTENSIONS = set(["zip"])


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


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

    breakpoint()

    if "file" not in request.files:
        flash("No file sent")
        return redirect(request.url)

    flash("I got a file")
    return render_template("upload.html")
    # file = request.files["file"]
    # if file.filename == "":
    #     flash("No file selected")
    #     return redirect(request.url)

    # if file and allowed_file(file.filename):
    #     filename = secure_filename(file.filename)
    #     file.save(os.path.join(UPLOAD_FOLDER, filename))
    #     zip_ref = zipfile.ZipFile(os.path.join(UPLOAD_FOLDER, filename), "r")
    #     zip_ref.extractall(UPLOAD_FOLDER)
    #     zip_ref.close()
    #     flash("Deployment succeeded.")
    #     return redirect(url_for("upload_file", filename=filename))
