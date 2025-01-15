from fastapi import HTTPException, status
from jose import ExpiredSignatureError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.schemas.auth_schema import AuthLogin, AuthRegister
from src.models import Usuario
from src.security import (
    decode_access_token,
    create_access_token,
    get_password_hash,
    verify_password,
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
        )
        db.add(db_usuario)
        await db.commit()
        await db.refresh(db_usuario)
        return db_usuario

    async def authenticate(self, login: AuthLogin, db: AsyncSession) -> str:
        usuario = await self.get_by_email(login.email, db)
        if not usuario or not verify_password(login.senha, usuario.senha):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token_data = {"sub": str(usuario.id), "role": usuario.role}
        access_token = create_access_token(token_data)
        return access_token

    async def refresh_token(self, current_token: str, db: AsyncSession) -> dict:
        try:
            payload = decode_access_token(current_token, verify_exp=False)
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Token inválido ou não contém informações do usuário.",
                )

            result = await db.execute(select(Usuario).where(Usuario.id == int(user_id)))
            user = result.scalars().first()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuário não encontrado.",
                )

            token_data = {"sub": user.id, "role": user.role}
            new_access_token = create_access_token(data=token_data)

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
