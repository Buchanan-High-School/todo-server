from todo_server import ma


class TodoSchema(ma.Schema):
    id = ma.Integer(dump_only=True)
    completed = ma.Boolean()
    created_at = ma.DateTime()
    description = ma.String()
    due = ma.DateTime()
    title = ma.String()


class CourseRecordSchema(ma.Schema):
    id = ma.Integer(dump_only=True)
    course = ma.String()
    topic = ma.String()
    period = ma.String()
    todo = ma.String()


class ThreadSchema(ma.Schema):
    id = ma.Integer(dump_only=True)
    title = ma.String()
    created_at = ma.DateTime()
    content = ma.String()
    author = ma.String()
    is_reply = ma.Boolean()
    is_approved = ma.Boolean()
