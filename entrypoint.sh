#!/bin/sh

echo "Executando no ambiente: $ENV_TYPE"

poetry run alembic upgrade head

if [ "$ENV_TYPE" = "dev" ]; then
  echo "Iniciando servidor com reload automático..."
  poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
else
  echo "Iniciando servidor em modo de produção..."
  poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000
fi