from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from src.controllers import (
    audio_controller,
    auth_controller,
    participante_controller,
    usuario_controller,
    vocalizacao_controller,
)
from src.security import get_api_key
from src.database import ENV_TYPE

app = FastAPI(
    title=f"VocalizeAI API - {ENV_TYPE.upper()}",
    description=f"API para o projeto VocalizeAI - Ambiente: {ENV_TYPE.upper()}",
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_environment_header(request, call_next):
    response = await call_next(request)
    response.headers["X-Environment"] = ENV_TYPE
    return response


app.include_router(
    audio_controller.router,
    prefix="/audios",
    tags=["Audios"],
    dependencies=[Depends(get_api_key)],
)
app.include_router(
    auth_controller.router,
    prefix="/auth",
    tags=["Auth"],
    dependencies=[Depends(get_api_key)],
)
app.include_router(
    participante_controller.router,
    prefix="/participantes",
    tags=["Participantes"],
    dependencies=[Depends(get_api_key)],
)
app.include_router(
    usuario_controller.router,
    prefix="/usuarios",
    tags=["Usuarios"],
    dependencies=[Depends(get_api_key)],
)
app.include_router(
    vocalizacao_controller.router,
    prefix="/vocalizacoes",
    tags=["Vocalizacoes"],
    dependencies=[Depends(get_api_key)],
)


@app.get("/", include_in_schema=True, tags=["Status"])
async def root():
    return {
        "status": "online",
        "message": f"VocalizeAI API está funcionando - Ambiente: {ENV_TYPE}",
        "environment": ENV_TYPE,
    }
