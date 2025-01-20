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


class UsuarioPayload(UsuarioBase):
    id: int
    role: str
    participante: Optional[ParticipanteResponse] = None

    
class UsuarioResponse(UsuarioBase):
    id: int
    role: str
    created_at: datetime
    updated_at: datetime
