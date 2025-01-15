from pydantic import BaseModel
from datetime import datetime


class AudioBase(BaseModel):
    nome_arquivo: str
    id_vocalizacao: int
    id_usuario: int


class AudioCreate(AudioBase):
    pass


class AudioResponse(AudioBase):
    id: int
    created_at: datetime
    updated_at: datetime
