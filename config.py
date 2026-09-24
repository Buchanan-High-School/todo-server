import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))


load_dotenv(os.path.join(basedir, ".env"))


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI")
    SQLALCHEMY_RECORD_QUERIES = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.environ.get("SECRET_KEY")
    LOGIN_TOKEN = os.environ.get("LOGIN_TOKEN")

    UPLOAD_PATH = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "todo_server", "user")
    )
