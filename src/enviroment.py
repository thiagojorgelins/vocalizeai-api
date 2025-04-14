import os
from dotenv import load_dotenv


def load_environment():
    env_type = os.environ.get("ENV_TYPE")

    if env_type == "dev":
        env_file = ".env.dev"
    else:
        env_file = ".env.main"

    load_dotenv(env_file)

    return env_type
