import os
import random
from datetime import UTC, datetime

import redis
from fastapi import HTTPException, status
from jose import ExpiredSignatureError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Usuario
from src.schemas.auth_schema import AuthLogin, AuthRegister, Token, RefreshTokenRequest
from src.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
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

    async def authenticate(self, login: AuthLogin, db: AsyncSession) -> dict:
        usuario = await self.get_by_email(login.email, db)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado.",
            )

        if not usuario.verificado:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário não verificado. Verifique seu e-mail para ativar sua conta.",
            )

        if not verify_password(login.senha, usuario.senha):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email e/ou senha inválidos.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return await self.generate_tokens(usuario)

    async def refresh_token(self, refresh_request: RefreshTokenRequest, db: AsyncSession) -> dict:
        try:
            # Decodificar o refresh token
            payload = decode_refresh_token(refresh_request.refresh_token)
            usuario_id = payload.get("sub")
            
            if not usuario_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token inválido ou não contém informações do usuário.",
                )

            # Verificar se o refresh token está armazenado no Redis
            stored_refresh_token = redis_client.get(f"refresh_token:{usuario_id}")
            if not stored_refresh_token or stored_refresh_token.decode("utf-8") != refresh_request.refresh_token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Sua sessão expirou. Faça login novamente.",
                )

            # Buscar o usuário no banco de dados
            result = await db.execute(
                select(Usuario).where(Usuario.id == int(usuario_id))
            )
            usuario = result.scalars().first()

            if not usuario:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuário não encontrado.",
                )

            # Invalidar o refresh token atual adicionando-o à blacklist
            await self.blacklist_token(refresh_request.refresh_token)
            
            # Gerar novos tokens
            new_tokens = await self.generate_tokens(usuario)
            
            return new_tokens

        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expirado. Faça login novamente.",
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

    async def generate_tokens(self, usuario: Usuario) -> dict:
        """Gera access token e refresh token para o usuário."""
        payload = {
            "sub": str(usuario.id),
            "email": usuario.email,
            "role": usuario.role,
        }

        access_token = create_access_token(payload)
        refresh_token = create_refresh_token(payload)

        # Armazenar o refresh token no Redis com expiração de 7 dias
        refresh_token_expiry = 7 * 24 * 60 * 60  # 7 dias em segundos
        redis_client.set(
            f"refresh_token:{usuario.id}",
            refresh_token,
            ex=refresh_token_expiry
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    async def blacklist_token(self, token: str) -> None:
        """Adiciona um token à blacklist no Redis."""
        try:
            # Decodificar o token para obter o tempo de expiração
            payload = decode_refresh_token(token, verify_exp=False)
            exp = payload.get("exp")
            
            if exp:
                now = datetime.now(UTC).timestamp()
                ttl = int(exp - now)
                
                if ttl > 0:
                    redis_client.set(f"blacklist:{token}", "1", ex=ttl)
        except:
            # Se não conseguir decodificar, adiciona com TTL padrão
            redis_client.set(f"blacklist:{token}", "1", ex=86400)  # 24 horas

    async def logout(self, usuario_id: int, access_token: str = None, refresh_token: str = None) -> dict:
        """Realiza logout invalidando os tokens."""
        try:
            # Invalidar access token se fornecido
            if access_token:
                await self.blacklist_token(access_token)
            
            # Invalidar refresh token se fornecido
            if refresh_token:
                await self.blacklist_token(refresh_token)
            
            # Remover refresh token do Redis
            redis_client.delete(f"refresh_token:{usuario_id}")
            
            return {"message": "Logout realizado com sucesso."}
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ocorreu um erro durante o logout. Sua sessão foi encerrada com segurança.",
            )

    def is_token_blacklisted(self, token: str) -> bool:
        """Verifica se um token está na blacklist."""
        return redis_client.exists(f"blacklist:{token}") > 0
