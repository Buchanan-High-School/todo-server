import os
import logging
from logging.handlers import RotatingFileHandler

import socketio

from flask import Flask, has_request_context, jsonify, request, render_template
from todo_server.exceptions import (
    bad_request,
    not_authorized,
    not_found,
    server_error,
    unprocessable_entity,
    unsupported_media_type,
)
from todo_server.extensions import db, login_manager, ma, migrate, sio
from todo_server.blueprints import chat, course_review, threads, todo

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

    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    login_manager.init_app(app)
    sio.init_app(app)

    # register error handlers
    app.register_error_handler(400, bad_request)
    app.register_error_handler(403, not_authorized)
    app.register_error_handler(404, not_found)
    app.register_error_handler(415, unsupported_media_type)
    app.register_error_handler(422, unprocessable_entity)
    app.register_error_handler(500, server_error)

    # register the routes
    app.register_blueprint(todo.bp)
    app.register_blueprint(chat.bp)
    app.register_blueprint(course_review.bp)
    app.register_blueprint(threads.bp)

    @app.before_request
    def preflight():
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        }
        if request.method.lower() == "options":
            return jsonify(headers), 200

    @app.after_request
    def add_cors_headers(response):
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add(
            "Access-Control-Allow-Methods", "GET, POST, PATCH, PUT, DELETE, OPTIONS"
        )
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type, Authorization"
        )
        return response

    @app.get("/")
    def index():
        return render_template("index.html"), 200

    return app
