from flask import Blueprint, render_template
from flask_socketio import emit, send

from todo_server.extensions import sio


bp = Blueprint("chat", __name__)


# Render the first page?
@bp.get("/chat")
def chat_index():
    print("loading chat")
    return render_template("chat/index.html")


@sio.on("connect")
def connected():
    emit("my_response", "Connected")


@sio.on("message")
def handle_message(data):
    emit("response", data)
