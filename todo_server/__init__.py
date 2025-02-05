import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, has_request_context, request
from todo_server.extensions import db, login_manager, ma, migrate
from todo_server.blueprints import todo

from config import Config


class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_address = request.remote_addr
        else:
            record.url = None
            record.remote_addr = None

        return super().format(record)


def create_app(config=Config):
    app = Flask(__name__, static_url_path="/static")
    app.config.from_object(config)
    if not app.debug and not app.testing:
        if not os.path.exists("log"):
            os.mkdir("log")

        formatter = RequestFormatter(
            "[%(asctime)s] %(remote_addr)s requested %(url)s\n"
            "%(levelname)s in %(module)s: %(message)s"
        )

        file_handler = RotatingFileHandler(
            "log/todo_server.log", maxBytes=10240, backupCount=10
        )

        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info("Starting todo_server")

    from todo_server import models

    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    login_manager.init_app(app)

    app.register_blueprint(todo.bp)

    return app
