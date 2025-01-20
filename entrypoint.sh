#!/bin/sh

poetry run alembic revision --autogenerate -m "initial migrations"

poetry run alembic upgrade head

poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
