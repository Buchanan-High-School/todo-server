from flask import abort, Blueprint, g, jsonify
from webargs import fields
from webargs.flaskparser import parser

from todo_server.extensions import db
from todo_server.models import Todo
from todo_server.schemas import TodoSchema
from todo_server.utils import clean_escaped_html

bp = Blueprint("todo", __name__)


# Catch any requests without the correct query param
@bp.before_request
def check_query_param():
    args = parser.parse({"Authorization": fields.Str()}, location="headers")
    if not args.get("Authorization"):
        abort(401, "Missing required Authorization header")
    else:
        g.current_user = str(args.get("Authorization").split(" ")[1])


# Set webargs to look at the `data` property of the request object
@parser.location_loader("data")
def load_data(request, schema):
    return request.json


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
    args = parser.parse(
        {
            "title": fields.Str(required=True),
            "description": fields.Str(),
            "due": fields.Date(),
            "completed": fields.Bool(),
        },
        location="data",
    )
    print(args)

    # Sanitize the string inputs.
    title = clean_escaped_html(args.get("title"))

    if args.get("description"):
        description = clean_escaped_html(args.get("description"))

    todo = Todo(user_id=g.current_user, **args)
    # todo = Todo(
    #     title=title,
    #     description=description,
    #     due=args.get("due"),
    #     user_id=g.current_user,
    # )
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

    args = parser.parse(
        {
            "title": fields.Str(),
            "description": fields.Str(),
            "due": fields.DateTime(),
            "completed": fields.Bool(),
        },
        location="data",
    )

    if not args:
        abort(400, "Empty JSON body.")

    if args:
        if args.get("title"):
            args["title"] = clean_escaped_html(args.get("title"))

        if args.get("description"):
            args["description"] = clean_escaped_html(args.get("description"))

        todo.update(args)

    return jsonify({"data": TodoSchema().dump(todo), "status": "success"}), 200


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
