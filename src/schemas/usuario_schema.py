from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class NivelSuporte(int, Enum):
    NIVEL_1 = 1
    NIVEL_2 = 2
    NIVEL_3 = 3


class GeneroParticipante(str, Enum):
    M = "Masculino"
    F = "Feminino"


class Condicao(str, Enum):
    TEA = "Transtorno do Espectro Autista"
    T21 = "Síndrome de Down"
    PC = "Paralisia Cerebral"
    OUTRA = "Outra"


class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr
    celular: str


class UsuarioUpdate(UsuarioBase):
    nome: Optional[str]
    email: Optional[EmailStr]
    celular: Optional[str]


class UsuarioResponse(UsuarioBase):
    id: int
    role: str
    created_at: datetime
    updated_at: datetime
