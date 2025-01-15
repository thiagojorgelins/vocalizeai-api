from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str


class Login(BaseModel):
    email: EmailStr
    senha: str
