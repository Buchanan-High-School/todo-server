from flask import Blueprint, jsonify


bp = Blueprint("auto", __name__)


@bp.get("/auth")
def auth_index():
    pass


@bp.post("/auth")
def request_token():
    pass
