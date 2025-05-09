from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr
    celular: str


class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    celular: Optional[str] = None


class ParticipanteResponse(BaseModel):
    id: int
    nome: str

    class Config:
        from_attributes = True


class UsuarioPayload(UsuarioBase):
    id: int
    role: str
    participantes: list[ParticipanteResponse] = []

    class Config:
        from_attributes = True


class UsuarioResponse(UsuarioBase):
    id: int
    role: str
    created_at: datetime
    updated_at: datetime
    verificado: bool
    aceite_termos: bool
