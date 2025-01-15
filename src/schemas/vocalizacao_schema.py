from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class VocalizacaoBase(BaseModel):
    nome: str
    descricao: Optional[str] = None


class VocalizacaoCreate(VocalizacaoBase):
    pass


class VocalizacaoResponse(VocalizacaoBase):
    id: int
    created_at: datetime
    updated_at: datetime
