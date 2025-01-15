from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ClassificacaoBase(BaseModel):
    id_usuario: int
    id_vocalizacao: int
    predicao_modelo: float
    avaliacao_usuario: Optional[str] = None


class ClassificacaoCreate(ClassificacaoBase):
    pass


class ClassificacaoResponse(ClassificacaoBase):
    id: int
    created_at: datetime
