import os
from config import Config
from dotenv import load_dotenv

from todo_server.extensions import sio

for env_file in ".env":
    env = os.path.join(os.getcwd(), env_file)
    if os.path.exists(env):
        load_dotenv(env)


from todo_server import create_app

if __name__ == "__main__":
    app = create_app(Config)
    sio.run(app, cors_allowed_origins="*")
