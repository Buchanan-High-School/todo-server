from flask import abort, Blueprint, current_app, g, jsonify, request
from webargs import fields
from webargs.flaskparser import parser

from todo_server.extensions import db
from todo_server.models import Todo
from todo_server.schemas import TodoSchema


bp = Blueprint("todo", __name__)


# Catch any requests without the correct query param
@bp.before_request
def check_query_param():
    args = parser.parse({"user": fields.Str()}, location="query")
    if not args.get("user"):
        abort(401, "Missing requried `user` parameter")
    else:
        g.current_user = args.get("user")


# Set webargs to look at the `data` property of the request object
@parser.location_loader("data")
def load_data(request, schema):
    return request.json


@bp.get("/")
def index():
    return f"Welcome {g.current_user}"


@bp.get("/todo")
def get_all_todo():
    """
    Return all todo items for a given user.
    """
    current_user = g.current_user
    user_todo = Todo.query.filter(Todo.user_id == current_user).all()
    return TodoSchema(many=True).dump(user_todo)


@bp.get("/todo/<int:todo_id>")
def get_single_todo(todo_id):
    pass


@bp.post("/todo")
def create_todo():
    args = parser.parse(
        {
            "title": fields.Str(required=True),
            "description": fields.Str(),
            "due": fields.DateTime(),
        },
        location="data",
    )
    args["user_id"] = g.current_user

    todo = Todo(
        title=args.get("title"),
        description=args.get("description"),
        due=args.get("due"),
        user_id=g.current_user,
    )
    db.session.add(todo)
    db.session.commit()

    todos = Todo.query.filter(Todo.user_id == args.get("user_id")).all()
    return TodoSchema(many=True).dump(todos)


@bp.put("/todo/<int:todo_id>")
def edit_todo(todo_id):
    pass


@bp.delete("/todo/<int:todo_id>")
def delete_todo(todo_id):
    pass
