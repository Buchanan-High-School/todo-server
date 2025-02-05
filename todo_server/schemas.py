from todo_server import ma


class TodoSchema(ma.Schema):
    id = ma.Integer(dump_only=True)
    completed = ma.Boolean()
    created_at = ma.DateTime()
    description = ma.String()
    due = ma.DateTime()
    title = ma.String()
