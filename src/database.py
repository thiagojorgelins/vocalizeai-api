import os
import socket
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


def load_environment():
    env_type = os.getenv("ENV_TYPE", "main").lower()

    if env_type == "dev":
        print("Carregando configuração DEV")
        env_file = ".env.dev"
    else:
        print("Carregando configuração MAIN")
        env_file = ".env.main"

    load_dotenv(env_file)

    return env_type


ENV_TYPE = load_environment()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()


async def get_db():
    async with async_session() as session:
        yield session
