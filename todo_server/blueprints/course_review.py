from flask import abort, Blueprint, g, jsonify, request
from webargs import fields
from webargs.flaskparser import parser

from todo_server.extensions import db
from todo_server.models import CourseRecord
from todo_server.schemas import CourseRecordSchema
from todo_server.utils import clean_escaped_html

bp = Blueprint("course-record", __name__)


@bp.before_request
def check_query_param():
    args = parser.parse({"Authorization": fields.Str()}, location="headers")
    if not args.get("Authorization"):
        abort(401, "Missing required Authorization header")
    else:
        g.current_user = str(args.get("Authorization").split(" ")[1])


@bp.get("/course-todo")
def get_all_course_todo():
    current_user = g.current_user
    user_todo = Todo.query.filter(CourseRecord.user_id == current_user).all()
    return (
        jsonify(
            {"data": CourseRecordSchema(many=True).dump(user_todo), "status": "success"}
        ),
        200,
    )


@bp.get("/course-todo/<int:todo_id>")
def get_single_course_todo(todo_id):
    todo = CourseRecord.query.filter(CourseRecord.id == todo_id).first()

    if not todo:
        abort(404)

    if todo.user_id != g.current_user:
        abort(403, "You are not authorized to access this item.")

    return jsonify({"data": CourseRecordSchema().dump(todo), "status": "success"}), 200


@bp.post("/course-todo")
def create_course_todo():
    args = request.json

    if not args.get("course"):
        abort(422, "Missing required 'course' argument.")

    # Sanitize the string inputs.
    args["course"] = clean_escaped_html(args.get("todo"))

    if args.get("description"):
        args["description"] = clean_escaped_html(args.get("description"))

    course_todo = CourseRecord(user_id=g.current_user, **args)
    db.session.add(todo)
    db.session.commit()

    todos = CourseRecord.query.filter(Todo.user_id == g.current_user).all()
    return (
        jsonify(
            {
                "created": CourseRecordSchema().dump(todo),
                "data": CourseRecordSchema(many=True).dump(todos),
                "status": "success",
            }
        ),
        200,
    )
