from pydantic import BaseModel
from datetime import datetime


class AudioBase(BaseModel):
    nome_arquivo: str
    id_usuario: int
    id_vocalizacao: int
    id_participante: int


class AudioCreate(AudioBase):
    pass


class AudioResponse(AudioBase):
    id: int
    id_usuario: int
    created_at: datetime
    updated_at: datetime
