from datetime import timedelta
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.models import Usuario
from src.schemas.usuario_schema import UsuarioUpdate


class UsuarioService:
    async def get_all(self, db: AsyncSession) -> list[Usuario]:
        result = await db.execute(
            select(Usuario).options(selectinload(Usuario.participante))
        )
        return result.scalars().all()

    async def get_one(self, id: int, db: AsyncSession) -> Usuario:
        return await self.__get_by_id(id, db)

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
