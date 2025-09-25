# VocalizeAI API

## 1. Tecnologias Utilizadas

Esta API foi desenvolvida para o projeto VocalizeAI, focada na coleta e processamento de vocalizações não verbais de indivíduos com Transtorno do Espectro Autista (TEA). O sistema permite o cadastro dos usuários e participantes, upload e segmentação de áudios, utilizando as seguintes tecnologias:

### Backend

- ![Python](https://img.shields.io/badge/-Python_3.11-3776AB?logo=python&logoColor=white&style=flat) (Linguagem principal)
- ![FastAPI](https://img.shields.io/badge/-FastAPI-009688?logo=fastapi&logoColor=white&style=flat) (Framework web assíncrono)
- ![Pydantic](https://img.shields.io/badge/-Pydantic-E92063?logo=pydantic&logoColor=white&style=flat) (Validação de dados e serialização)
- ![SQLAlchemy](https://img.shields.io/badge/-SQLAlchemy-D71F00?logo=sqlalchemy&logoColor=white&style=flat) (ORM para banco de dados)
- ![Alembic](https://img.shields.io/badge/-Alembic-FF6B6B?logo=alembic&logoColor=white&style=flat) (Migrações de banco de dados)

### Banco de Dados

- ![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-336791?logo=postgresql&logoColor=white&style=flat) (Banco de dados relacional)
- ![Redis](https://img.shields.io/badge/-Redis-DC382D?logo=redis&logoColor=white&style=flat) (Cache e sessões)

### Processamento de Áudio

- ![FFmpeg](https://img.shields.io/badge/-FFmpeg-007808?logo=ffmpeg&logoColor=white&style=flat) (Processamento de áudio)
- **PyDub** (Manipulação de áudio em Python)

### Infraestrutura

- ![Docker](https://img.shields.io/badge/-Docker-2496ED?logo=docker&logoColor=white&style=flat) e ![Docker Compose](https://img.shields.io/badge/-Docker%20Compose-2496ED?logo=docker&logoColor=white&style=flat) (Conteinerização)
- ![Poetry](https://img.shields.io/badge/-Poetry-60A5FA?logo=poetry&logoColor=white&style=flat) (Gerenciamento de dependências)

### Serviços Externos

- ![AWS S3](https://img.shields.io/badge/-AWS_S3-FF9900?logo=amazon-aws&logoColor=white&style=flat) (Armazenamento de arquivos)
- **Brevo** (Envio de emails)

## 2. Arquitetura da Solução

A aplicação segue uma arquitetura modular baseada em camadas:

```
src/
├── controllers/     # Endpoints da API (Camada de apresentação)
├── services/        # Lógica de negócios (Camada de serviços)
├── models/          # Modelos de dados (Camada de dados)
├── schemas/         # Validação e serialização (Pydantic)
├── preprocessing/   # Processamento de áudio
├── utils/          # Utilitários gerais
└── security.py     # Autenticação e autorização
```

### Componentes Principais

1. **API REST**: Endpoints para gerenciamento de usuários, participantes, vocalizações e áudio
2. **Sistema de Autenticação**: JWT tokens com diferentes níveis de acesso
3. **Processamento de Áudio**: Segmentação automática de áudios, removendo partes silenciosas e dividindo em segmentos com conteúdo sonoro
4. **Redis**: Armazenamento temporário de códigos de verificação para email e gerenciamento de tokens de logout
5. **Banco de Dados**: PostgreSQL com migrações automáticas via Alembic

## 3. Funcionalidades da API

### Autenticação
- **POST** `/auth/login` - Login de usuários
- **POST** `/auth/register` - Registro de novos usuários
- **POST** `/auth/refresh` - Gera um novo token se o Refresh token ainda for válido
- **POST** `/auth/password-reset` - Envia um código ao email do usuário para fazer a troca da senha
- **POST** `/auth/confirm-password-reset` - Alterar a senha após confirmar o código
- **POST** `/auth/confirm-registration` - Confirmar o usuário com o código enviado para o email ao tentar se registrar
- **POST** `/auth/resend-confirmation-code` - Enviar um novo código em alguma situação em que o usuário deixar o código expirarr
- **POST** `/auth/logout` - Logout invalidando o _access_token_ e o _refresh_token_ do usuário

### Usuários
- **GET** `/usuarios` - Listagens dos usuários (ADMIN)
- **GET** `/usuarios/{id}` - Detalhes de um usuário
- **PATCH** `/usuarios/{id}` - Atualizar os dados do usuário
- **DELETE** `/usuarios{id}` - Deletar um usuário (ADMIN)

### Participantes
- **POST** `/participantes` - Cadastro de participantes
- **GET** `/participantes` - Listagem de participantes (ADMIN)
- **GET** `/participantes/{id}` - Detalhes de um participante
- **GET** `/participantes/usuario/{usuario_id}` - Lista os participantes do usuário
- **PATCH** `/participantes/{id}` - Atualização de participante
- **DELETE** `/participantes/{id}` - Exclusão de participante (ADMIN)

### Vocalizações
- **POST** `/vocalizacoes` - Cadastro de um novo rótulo de vocalização
- **GET** `/vocalizacoes` - Listagem dos rótulos vocalizações
- **GET** `/vocalizacoes/{id}` - Detalhes de um rótulo de vocalização
- **PATCH** `/vocalizacoes/{id}` - Atualização de um rótulo de vocalização
- **DELETE** `/vocalizacoes/{id}` - Exclusão de um rótulo de vocalização

### Áudios
- **POST** `/audios` - Upload de um ou mais arquivos de áudio para o bucket S3
- **PATCH** `/audios/{id}` - Atualiza um áudio específico, incluindo a possibilidade de alterar a vocalização e renomear o arquivo no S3 de acordo com o novo rótulo
- **POST** `/audios/{id}` - Deletar um arquivo de áudio
- **GET** `/audios/{id}/play` - Retorna a URL de um áudio específico do S3 para poder reproduzi-lo. Verifica o cabeçalho 'x-environment' para decidir qual bucket usar.
- **GET** `/audios/usuario/{id_usuario}` - Lista todos os áudios associados a um usuário
- **DELETE** `/audios/usuario/{id_usuario}` - Deleta todos os áudios associados a um usuário
- **GET** `/audios/participante/{id_participante}` - Lista todos os áudios associados a um participante
- **DELETE** `/audios/parrticipante/{id_participante}` - Deleta todos os áudios associados a um participante
- **GET** `/audios/amount/participante/{id_participante}` - Retorna a quantidade de áudios associados a um participante
## 4. Variáveis de Ambiente

As seguintes variáveis devem ser configuradas:

```env
API_KEY=minha_api_key

# JWT
SECRET_KEY=secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_SECRET_KEY=refresh_secret_key
REFRESH_TOKEN_EXPIRE_DAYS=7

# Banco de dados
DATABASE_URL=postgresql+asyncpg://db_username:db_password@cauta_database:5432/my_db
POSTGRES_USER=db_username
POSTGRES_PASSWORD=db_password
POSTGRES_DB=my_db

# Redis
REDIS_PORT=6379
REDIS_HOST=cauta_redis

# Brevo
BREVO_API_KEY=
BREVO_SENDER_EMAIL=
BREVO_SENDER_NAME=

# AWS S3
S3_BUCKET_NAME=bucket_name
AWS_ACCESS_KEY_ID=access_key_id
AWS_SECRET_ACCESS_KEY=aws_secret_access_key
AWS_DEFAULT_REGION=us-east-1
```

### Scripts Automatizados

- `migrate.sh`: Script para executar migrações automaticamente
- `setup-environments.sh`: Configuração inicial dos ambientes
- `run.sh`: Script para iniciar um dos ambientes do projeto(main ou dev)

## 5. Como Executar o Projeto

### Pré-requisitos

- ![Docker](https://img.shields.io/badge/-Docker-2496ED?logo=docker&logoColor=white&style=flat) Docker
- ![Docker Compose](https://img.shields.io/badge/-Docker%20Compose-2496ED?logo=docker&logoColor=white&style=flat) Docker Compose
- ![Git](https://img.shields.io/badge/-Git-F05032?logo=git&logoColor=white&style=flat) Git

### Instalação e Execução

1. **Clone o repositório**
```bash
git clone https://github.com/thiagojorgelins/vocalizeai-api
cd vocalizeai-api
```

2. **Configure as variáveis de ambiente**
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

3. **Execute o ambiente de desenvolvimento**
```bash
./setup-environments.sh # Será criado um .env para cada ambiente(main e dev)

./run.sh dev # Rodar o ambiente de desenvolvimento
./run.sh main # Rodar o ambiente de produção
./run.sh rebuild-main # Recriar a imagem do container de produção
./run.sh stop-main # Parar os containers do ambiente de produção
./run.sh stop-dev # Parar os containers do ambiente de desenvolvimento
./run.sh stop-all # Parar ambos ambientes
```

5. **Acesse a documentação da API**
```
http://localhost:8000/docs
```

## 6. Configuração de Ambientes

O projeto oferece dois ambientes distintos com configurações otimizadas para diferentes cenários:

#### Ambiente de Desenvolvimento (`dev`)
- **Hot Reload**: O diretório do projeto está mapeado como volume, permitindo que todas as alterações no código sejam refletidas automaticamente sem necessidade de rebuild
- **Porta**: 8001
- **Banco de Dados**: PostgreSQL na porta 5433
- **Redis**: Porta 6380

#### Ambiente de Produção (`main`)  
- **Performance Otimizada**: Imagem Docker otimizada para produção
- **Porta**: 8000
- **Atualizações**: Requer rebuild da imagem para aplicar alterações no código

> No ambiente de produção, sempre execute `./run.sh rebuild-main` após alterações no código para garantir que as mudanças sejam aplicadas.