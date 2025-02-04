from todo_server import ma


class TodoSchema(ma.Schema):
    id = ma.Integer(dump_only=True)
    title = ma.String()
    description = ma.String()
    due = ma.DateTime()
    created_at = ma.DateTime()
