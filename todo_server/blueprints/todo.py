from datetime import date, timedelta

from flask import abort, Blueprint, g, jsonify, request
from webargs import fields
from webargs.flaskparser import parser

from todo_server.extensions import db
from todo_server.models import Todo
from todo_server.schemas import TodoSchema
from todo_server.utils import clean_escaped_html

bp = Blueprint("todo", __name__)


# Handle missing due dates on the request object
def default_due():
    valid = date.today() + timedelta(days=1)
    return valid


# Catch any requests without the correct query param
@bp.before_request
def check_query_param():
    args = parser.parse({"Authorization": fields.Str()}, location="headers")
    if not args.get("Authorization"):
        abort(401, "Missing required Authorization header")
    else:
        g.current_user = str(args.get("Authorization").split(" ")[1])


@bp.get("/todo")
def get_all_todo():
    """
    Return all todo items for a given user.
    """
    current_user = g.current_user
    user_todo = Todo.query.filter(Todo.user_id == current_user).all()
    return (
        jsonify({"data": TodoSchema(many=True).dump(user_todo), "status": "success"}),
        200,
    )


@bp.get("/todo/<int:todo_id>")
def get_single_todo(todo_id):
    todo = Todo.query.filter(Todo.id == todo_id).first()

    if not todo:
        abort(404)

    if todo.user_id != g.current_user:
        abort(403, "You are not authorized to access this item.")

    return jsonify({"data": TodoSchema().dump(todo), "status": "success"}), 200


@bp.post("/todo")
def create_todo():
    args = request.json

    if not args.get("title"):
        abort(422, "Missing required 'title' argument.")

    if not args.get("due"):
        args["due"] = default_due()

    # Sanitize the string inputs.
    title = clean_escaped_html(args.get("title"))

    if args.get("description"):
        description = clean_escaped_html(args.get("description"))

    todo = Todo(user_id=g.current_user, **args)
    db.session.add(todo)
    db.session.commit()

    todos = Todo.query.filter(Todo.user_id == g.current_user).all()
    return (
        jsonify(
            {
                "created": TodoSchema().dump(todo),
                "data": TodoSchema(many=True).dump(todos),
                "status": "success",
            }
        ),
        200,
    )


@bp.put("/todo/<int:todo_id>")
def edit_todo(todo_id):
    todo = Todo.query.filter(Todo.id == todo_id).first()
    if not todo:
        abort(404, "There is no item with that ID.")

    if todo.user_id != g.current_user:
        abort(403, "You are not authorized to access this item.")

    args = request.json

    if not args:
        abort(400, "Empty JSON body.")

    # Sanitize the string inputs.
    if args:
        if args.get("title"):
            args["title"] = clean_escaped_html(args.get("title"))

        if args.get("description"):
            args["description"] = clean_escaped_html(args.get("description"))

        todo.update(args)

    # return the entire list again
    todos = Todo.query.filter(Todo.user_id == g.current_user).all()

    return (
        jsonify(
            {
                "updated": TodoSchema().dump(todo),
                "data": TodoSchema(many=True).dump(todos),
                "status": "success",
            }
        ),
        204,
    )


@bp.delete("/todo/<int:todo_id>")
def delete_todo(todo_id):
    todo = Todo.query.filter(Todo.id == todo_id).first()

    if not todo:
        abort(404, "There is no item with that ID.")

    if todo.user_id != g.current_user:
        abort(403, "You are not authorized to access this item.")

    db.session.delete(todo)
    db.session.commit()

    # return the new array of items
    todos = Todo.query.filter(Todo.user_id == g.current_user).all()

    return (
        jsonify({"data": TodoSchema(many=True).dump(todos), "status": "success"}),
        200,
    )
