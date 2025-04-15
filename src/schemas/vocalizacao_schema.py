from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class VocalizacaoBase(BaseModel):
    nome: str
    descricao: str


class VocalizacaoCreate(VocalizacaoBase):
    pass


class VocalizacaoUpdate(BaseModel):
    nome: Optional[str]
    descricao: Optional[str]


class VocalizacaoResponse(VocalizacaoBase):
    id: int
    id_usuario: int
    created_at: datetime
    updated_at: datetime
