from flask import jsonify


def not_found(e):
    return jsonify(
        {
            "message": "No todo found with that id.",
            "status": "error"
        }
    ), 404


def not_authorized(e):
    return jsonify(
        {
            "message": "You are not authorized to access that item.",
            "status": "error"
        }
    ), 403


def unprocessable_entity(e):
    headers = e.data.get("headers", None)
    messages = e.data.get("messages", ["Invalid request."])
    if headers:
        return jsonify(
            {
                "message": messages,
                "status": "error"
            }
        ), e.code, headers
    else:
        return jsonify(
            {
                "message": messages,
                "status": "error"
            }
        ), e.code


def unsupported_media_type(e):
    return jsonify(
        {
            "message": e.description,
            "status": "error"
        }
    ), 415


def bad_request(e):
    if e.description:
        message = e.description
    else:
        message = "Failed to decode JSON object. Did you stringify?"

    return jsonify(
        {
            "message": message,
            "status": "error"
        }
    ), 400


def server_error(e):
    return jsonify(
        {
            "message": "This isn't your fault. Let Mr. Bennett know.",
            "status": "error"
        }
    ), 500
