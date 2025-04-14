#!/bin/bash

if [ $# -lt 2 ]; then
    echo "Uso: ./migrate.sh [env] [comando] [args]"
    echo "  env: main ou dev"
    echo "  comando: "
    echo "    - generate [nome_da_migração]: gera uma nova migração"
    echo "    - upgrade: executa todas as migrações pendentes (upgrade head)"
    echo "    - downgrade [versão]: faz downgrade para a versão especificada"
    echo ""
    echo "Exemplos:"
    echo "  ./migrate.sh dev generate add_new_column"
    echo "  ./migrate.sh main upgrade"
    echo "  ./migrate.sh dev downgrade -1"
    exit 1
fi

ENV=$1
COMMAND=$2
CONTAINER_NAME="vocalizeai_backend"

if [ "$ENV" == "dev" ]; then
    CONTAINER_NAME="vocalizeai_backend_dev"
elif [ "$ENV" == "main" ]; then
    CONTAINER_NAME="vocalizeai_backend"
else
    echo "Ambiente inválido. Use 'main' ou 'dev'"
    exit 1
fi

if [ "$(docker ps -q -f name=$CONTAINER_NAME)" == "" ]; then
    echo "Container $CONTAINER_NAME não está rodando."
    echo "Inicie o ambiente primeiro com ./run.sh $ENV"
    exit 1
fi

case "$COMMAND" in
    "generate")
        if [ $# -lt 3 ]; then
            echo "Nome da migração não especificado"
            echo "Uso: ./migrate.sh $ENV generate [nome_da_migração]"
            exit 1
        fi
        MIGRATION_NAME=$3
        echo "Gerando migração '$MIGRATION_NAME' no ambiente $ENV..."
        docker exec $CONTAINER_NAME poetry run alembic revision --autogenerate -m "$MIGRATION_NAME"
        ;;
    "upgrade")
        echo "Executando upgrade no ambiente $ENV..."
        docker exec $CONTAINER_NAME poetry run alembic upgrade head
        ;;
    "downgrade")
        if [ $# -lt 3 ]; then
            echo "Versão para downgrade não especificada"
            echo "Uso: ./migrate.sh $ENV downgrade [versão]"
            exit 1
        fi
        VERSION=$3
        echo "Executando downgrade para versão '$VERSION' no ambiente $ENV..."
        docker exec $CONTAINER_NAME poetry run alembic downgrade $VERSION
        ;;
    *)
        echo "Comando inválido: $COMMAND"
        echo "Comandos válidos: generate, upgrade, downgrade"
        exit 1
        ;;
esac

echo "Operação concluída!"