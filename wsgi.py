import os
from config import Config
from dotenv import load_dotenv

from todo_server.extensions import sio
from todo_server import create_app

for env_file in ".env":
    env = os.path.join(os.getcwd(), env_file)
    if os.path.exists(env):
        load_dotenv(env)


if __name__ == "__main__":
    app = create_app(Config)
    sio.run(app)
else:
    gunicorn_app = create_app()
    sio.run(gunicorn_app, host="127.0.0.1", port=5000, use_reloader=False)
