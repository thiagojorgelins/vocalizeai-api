from pydantic import BaseModel, EmailStr

from src.schemas.usuario_schema import UsuarioBase


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str = None


class AuthRegister(UsuarioBase):
    senha: str
    aceite_termos: bool


class AuthLogin(BaseModel):
    email: EmailStr
    senha: str


class ConfirmRegistration(BaseModel):
    email: EmailStr
    codigo_confirmacao: str


class EmailRequest(BaseModel):
    email: EmailStr


class ResetPassword(BaseModel):
    email: EmailStr
    codigo_confirmacao: str
    nova_senha: str
