from pydantic import BaseModel, EmailStr

from src.schemas.usuario_schema import UsuarioBase


class Token(BaseModel):
    access_token: str


class AuthRegister(UsuarioBase):
    senha: str


class AuthLogin(BaseModel):
    email: EmailStr
    senha: str
