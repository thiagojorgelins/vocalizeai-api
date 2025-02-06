import os
import random

import redis
from fastapi import HTTPException, status
from jose import ExpiredSignatureError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Usuario
from src.schemas.auth_schema import AuthLogin, AuthRegister, ConfirmRegistration, Token
from src.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)
from src.utils.email_utils import send_confirmation_email, send_password_reset_email

redis_client = redis.StrictRedis(
    host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), db=0
)


class AuthService:
    async def get_by_email(self, email: str, db: AsyncSession) -> Usuario:
        result = await db.execute(select(Usuario).where(Usuario.email == email))
        return result.scalars().first()

    async def register(self, usuario: AuthRegister, db: AsyncSession) -> Usuario:
        email_exists = await self.get_by_email(usuario.email, db)
        if email_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado.",
            )

        hashed_password = get_password_hash(usuario.senha)
        db_usuario = Usuario(
            nome=usuario.nome,
            email=usuario.email,
            senha=hashed_password,
            celular=usuario.celular,
            verificado=False,
            aceite_termos=usuario.aceite_termos,
        )
        db.add(db_usuario)
        await db.commit()
        await db.refresh(db_usuario)

        confirmation_code = random.randint(100000, 999999)
        redis_client.set(
            name=f"confirmation_code:{usuario.email}", ex=900, value=confirmation_code
        )
        await send_confirmation_email(usuario.email, confirmation_code)

        return db_usuario

    async def confirm_registration(
        self, email: str, code: int, db: AsyncSession
    ) -> Usuario:
        usuario = await self.get_by_email(email, db)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado.",
            )

        if not self.verify_confirmation_code(email, code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Código de confirmação inválido.",
            )

        usuario.verificado = True
        await db.commit()
        return usuario

    async def authenticate(self, login: AuthLogin, db: AsyncSession) -> str:
        usuario = await self.get_by_email(login.email, db)
        if not usuario or not verify_password(login.senha, usuario.senha):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not usuario.verificado:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário não verificado. Verifique seu e-mail para ativar sua conta.",
            )

        token_data = {"sub": str(usuario.id), "role": usuario.role}
        access_token = create_access_token(token_data)
        return access_token

    async def refresh_token(self, current_token: Token, db: AsyncSession) -> dict:
        try:
            payload = decode_access_token(current_token.access_token, verify_exp=False)
            usuario_id = payload.get("sub")
            if not usuario_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Token inválido ou não contém informações do usuário.",
                )

            result = await db.execute(
                select(Usuario).where(Usuario.id == int(usuario_id))
            )
            usuario = result.scalars().first()

            if not usuario:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuário não encontrado.",
                )

            token_data = {"sub": str(usuario.id), "role": usuario.role}
            new_access_token = create_access_token(token_data)

            return {"access_token": new_access_token}

        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado. Faça login novamente.",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Erro ao renovar o token: {str(e)}",
            )

    async def resend_confirmation_code(self, email: str, db: AsyncSession):
        usuario = await self.get_by_email(email, db)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado.",
            )

        if usuario.verificado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuário já verificado.",
            )

        confirmation_code = random.randint(100000, 999999)
        redis_client.set(
            name=f"confirmation_code:{email}", ex=900, value=confirmation_code
        )
        await send_confirmation_email(email, confirmation_code)

    def verify_confirmation_code(self, email: str, code: int) -> bool:
        stored_code = redis_client.get(f"confirmation_code:{email}")
        if stored_code is None:
            return False
        return stored_code.decode("utf-8") == code

    async def request_password_reset(self, email: str, db: AsyncSession):
        usuario = await self.get_by_email(email, db)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado.",
            )

        reset_code = random.randint(100000, 999999)
        redis_client.set(name=f"reset_code:{email}", ex=900, value=reset_code)
        await send_password_reset_email(email, reset_code)

    async def confirm_password_reset(
        self, email: str, code: int, nova_senha: str, db: AsyncSession
    ):
        if not self.verify_reset_code(email, code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Código de redefinição inválido.",
            )

        usuario = await self.get_by_email(email, db)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado.",
            )

        usuario.senha = get_password_hash(nova_senha)
        await db.commit()

    def verify_reset_code(self, email: str, code: int) -> bool:
        stored_code = redis_client.get(f"reset_code:{email}")
        if stored_code is None:
            return False
        return stored_code.decode("utf-8") == code
