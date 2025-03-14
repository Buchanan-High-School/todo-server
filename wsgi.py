import os
from config import Config
from dotenv import load_dotenv

from todo_server import create_app

for env_file in ".env":
    env = os.path.join(os.getcwd(), env_file)
    if os.path.exists(env):
        load_dotenv(env)


app = create_app(Config)
