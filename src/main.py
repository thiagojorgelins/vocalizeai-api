from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer

from src.controllers import (
    audio_controller,
    auth_controller,
    participante_controller,
    usuario_controller,
    vocalizacao_controller,
)

app = FastAPI(title="CAUTA API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(audio_controller.router, prefix="/audios", tags=["Audios"])
app.include_router(auth_controller.router, prefix="/auth", tags=["Auth"])
app.include_router(
    participante_controller.router, prefix="/participantes", tags=["Participantes"]
)
app.include_router(usuario_controller.router, prefix="/usuarios", tags=["Usuarios"])
app.include_router(
    vocalizacao_controller.router, prefix="/vocalizacoes", tags=["Vocalizacoes"]
)
