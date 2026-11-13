import os
import shutil
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


def is_safe_path(base_dir, path, follow_symlinks=True):
    if follow_symlinks:
        matchpath = os.path.realpath(path)
    else:
        matchpath = os.path.abspath(path)
    return os.path.commonpath([base_dir, matchpath]) == base_dir


def get_common_root(zip_ref):
    """
    Extract a file and remove the common root from the zipped file. This is to prevent a second-level folder from being created inside the project directory the user specifies.
    """
    # Start by making a set of all the first prefixes
    top_levels = set()
    for info in zip_ref.infolist():
        # Remove any Mac metadata folders. Shame on you.
        if info.filename.startswith("__MACOSX") or info.filename.endswith(".DS_STORE"):
            continue
        parts = info.filename.split("/")
        if parts[0]:
            top_levels.add(parts[0])

    # only strip if there is one root directory with items. This preserves other nested directory paths
    if len(top_levels) == 1:
        root = top_levels.pop()
        if any(info.filename.startswith(f"{root}/") for info in zip_ref.infolist()):
            return f"{root}/"
        return ""


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
        return redirect(request.url), 400

    file = request.files["file"]
    if file.filename == "":
        flash("No file selected")
        return redirect(request.url), 400

    if not request.form.get("name"):
        flash("No project name given. Please enter a name for your published project.")
        return redirect(request.url), 400

    if not (file and allowed_file(file.filename)):
        flash("Only .zip files are allowed.")
        return redirect(request.url), 400

    if file and allowed_file(file.filename):
        safe_filename = secure_filename(file.filename).split(".")[0]
        safe_project_name = secure_filename(request.form.get("name")).lower()

        # Check that the user's directory exists.
        user_dir = get_user_dir(current_user)

        # Set a variable for the project path to use when saving the extracted zip.
        project_path = os.path.join(user_dir, safe_project_name)

        if os.path.isdir(project_path):
            flash(
                "A project with that name already exists. Use a different project name."
            )
            return render_template("upload.html"), 409

        # zip_filename = "{}.zip".format(safe_project_name)
        # zip_path = os.path.join(user_dir, zip_filename)
        # # file.save(zip_path)

        # Extract and flatten
        try:
            with zipfile.ZipFile(file.stream, "r") as zip_ref:
                root_prefix = get_common_root(zip_ref)
                print(root_prefix)

                for member in zip_ref.infolist():
                    if member.filename.startswith(
                        "__MACOSX"
                    ) or member.filename.endswith(".DS_STORE"):
                        continue

                    # Strip any top level folders from the path
                    rel_path = member.filename
                    print(member.filename)
                    if root_prefix and rel_path.startswith(root_prefix):
                        rel_path = rel_path[len(root_prefix) :]

                    if not rel_path:
                        continue

                    destination_path = os.path.join(project_path, rel_path)

                    if not is_safe_path(project_path, destination_path):
                        flash("There is an illegal file path in the zip")
                        return render_template("upload.html"), 400

                    # Make subdirectories or unzip files
                    if member.is_dir():
                        os.makedirs(destination_path, exist_ok=True)
                    else:
                        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
                        with (
                            zip_ref.open(member) as source,
                            open(destination_path, "wb") as target,
                        ):
                            shutil.copyfileobj(source, target)
        except zipfile.BadZipFile:
            flash("Invalid or corrupted .zip file.")
            return render_template("upload.html"), 400

        # Get the published URL for the file
        live_url = "/serve/{}/{}".format(
            current_user.last_name.lower(), safe_project_name
        )
        # Finally, save it to the database against the current user
        project = Project(name=safe_filename, owner=current_user.id, live_url=live_url)

        db.session.add(project)
        db.session.commit()

        message = Markup(
            "View your project at <a href='{}' target='_blank'>{}</a>".format(
                live_url, live_url
            )
        )
        flash(message)
        return redirect(url_for("deploy.upload"))


@bp.route(
    "/serve/<string:last_name>/<string:name>/", defaults={"filename": "index.html"}
)
@bp.route("/serve/<string:last_name>/<string:name>/<path:filename>")
def serve_extracted_files(last_name, name, filename):
    safe_user_id = secure_filename(last_name)
    safe_name = secure_filename(name)

    target_dir = os.path.join(
        current_app.config["UPLOAD_PATH"], safe_user_id, safe_name
    )

    if not os.path.exists(target_dir):
        return render_template("404.html"), 404

    return send_from_directory(target_dir, filename)


@bp.get("/projects")
def get_projects():
    # Get all deployed projects for quick management
    pass
