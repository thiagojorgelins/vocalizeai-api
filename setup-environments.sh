#!/bin/bash

if [ ! -f ".env" ]; then
    echo "Arquivo .env não encontrado. Verifique se você está no diretório raiz do projeto."
    exit 1
fi

echo "Criando arquivo .env.main..."
cp .env .env.main

echo "Criando arquivo .env.dev..."
cp .env .env.dev

sed -i 's/vocalizeai_database/vocalizeai_database_dev/g' .env.dev
sed -i 's/vocalizeai_redis/vocalizeai_redis_dev/g' .env.dev
sed -i 's/vocalizeai$/vocalizeai_dev/g' .env.dev

echo "Configurando permissões do script run.sh..."
chmod +x run.sh

echo "Configuração concluída!"
echo "Para iniciar o ambiente main, execute: ./run.sh main"
echo "Para iniciar o ambiente dev, execute: ./run.sh dev"