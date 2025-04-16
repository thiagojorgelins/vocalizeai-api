#!/bin/bash

ENV=$1

if [ "$ENV" == "main" ]; then
    echo "Iniciando ambiente MAIN..."
    docker-compose -f docker-compose.main.yml up -d
    echo "Aguardando inicialização do banco de dados..."
    sleep 5
    echo "Executando migrações no ambiente MAIN..."
    docker exec vocalizeai_backend sh -c "cd /app && poetry run alembic upgrade head"

elif [ "$ENV" == "rebuild-main" ]; then
    echo "Reconstruindo imagem e iniciando ambiente MAIN..."
    docker-compose -f docker-compose.main.yml build --no-cache
    docker-compose -f docker-compose.main.yml up -d
    echo "Aguardando inicialização do banco de dados..."
    sleep 5
    echo "Executando migrações no ambiente MAIN..."
    docker exec vocalizeai_backend sh -c "cd /app && poetry run alembic upgrade head"

elif [ "$ENV" == "dev" ]; then
    echo "Iniciando ambiente DEV..."
    docker-compose -f docker-compose.dev.yml up -d
    echo "Aguardando inicialização do banco de dados..."
    sleep 5
    echo "Executando migrações no ambiente DEV..."
    docker exec vocalizeai_backend_dev sh -c "cd /app && poetry run alembic upgrade head"

elif [ "$ENV" == "stop-main" ]; then
    echo "Parando ambiente MAIN..."
    docker-compose -f docker-compose.main.yml down

elif [ "$ENV" == "stop-dev" ]; then
    echo "Parando ambiente DEV..."
    docker-compose -f docker-compose.dev.yml down

elif [ "$ENV" == "stop-all" ]; then
    echo "Parando todos os ambientes..."
    docker-compose -f docker-compose.main.yml down
    docker-compose -f docker-compose.dev.yml down

else
    echo "Uso: ./run.sh [main|rebuild-main|dev|stop-main|stop-dev|stop-all]"
    exit 1
fi
