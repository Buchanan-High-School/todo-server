from datetime import date, timedelta

from flask import abort, Blueprint, g, jsonify, request
from webargs import fields
from webargs.flaskparser import parser

from todo_server.extensions import db
from todo_server.models import Thread
from todo_server.schemas import ThreadSchema
from todo_server.utils import clean_escaped_html

bp = Blueprint("threads", __name__)


@bp.get("/threads")
def get_all_threads():
    threads = Thread.query.all()
    return (
        jsonify({"data": ThreadSchema(many=True).dump(threads), "status": "success"}),
        200,
    )


@bp.get("/threads/<int:thread_id>")
def get_single_thread(thread_id):
    thread = Thread.query.filter(Thread.id == thread_id).first()

    if not thread:
        abort(404)

    return jsonify({"data": ThreadSchema().dump(thread), "status": "success"}), 200


@bp.post("/threads")
def create_thread():
    args = request.json

    if not args.get("title"):
        abort(422, "Missing required 'title' argument.")

    if not args.get("due"):
        args["due"] = default_due()

    # Sanitize the string inputs.
    title = clean_escaped_html(args.get("title"))

    if args.get("content"):
        description = clean_escaped_html(args.get("description"))

    thread = Thread(user_id=g.current_user, **args)
    db.session.add(thread)
    db.session.commit()

    threads = Thread.query.all()
    return (
        jsonify(
            {
                "created": ThreadSchema().dump(thread),
                "data": ThreadSchema(many=True).dump(threads),
                "status": "success",
            }
        ),
        200,
    )
