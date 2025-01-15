from datetime import timedelta
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.models import Usuario
from src.schemas.auth_schema import Login
from src.schemas.usuario_schema import UsuarioBase, UsuarioCreate, UsuarioUpdate
from src.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)


class UsuarioService:
    async def get_all(self, db: AsyncSession) -> list[Usuario]:
        result = await db.execute(
            select(Usuario).options(selectinload(Usuario.participante))
        )
        return result.scalars().all()

    async def get_one(self, id: int, db: AsyncSession) -> Usuario:
        return await self.__get_by_id(id, db)

    async def __get_by_email(self, email: str, db: AsyncSession) -> Usuario:
        result = await db.execute(select(Usuario).where(Usuario.email == email))
        return result.scalars().first()

    async def register(self, usuario: UsuarioCreate, db: AsyncSession) -> Usuario:
        email_exists = await self.__get_by_email(usuario.email, db)
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

    async def authenticate(self, login: Login, db: AsyncSession) -> str:
        usuario = await self.__get_by_email(login.email, db)
        if not usuario or not verify_password(login.senha, usuario.senha):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token_data = {"sub": str(usuario.id), "role": usuario.role}
        access_token = create_access_token(token_data)
        return access_token

    async def __get_by_id(self, id: int, db: AsyncSession) -> Usuario:
        result = await db.execute(select(Usuario).where(Usuario.id == id))
        usuario = result.scalars().first()
        if usuario is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado.",
            )
        return usuario

    async def update(
        self, id: int, usuario: UsuarioUpdate, db: AsyncSession
    ) -> Usuario:
        usuario_db = await self.__get_by_id(id, db)
        usuario_db.nome = usuario.nome
        usuario_db.email = usuario.email
        usuario_db.celular = usuario.celular
        await db.commit()
        await db.refresh(usuario_db)
        return usuario_db

    async def delete(self, id: int, db: AsyncSession) -> None:
        usuario = await self.__get_by_id(id, db)
        await db.delete(usuario)
        await db.commit()
