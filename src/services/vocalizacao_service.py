from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models import Vocalizacao
from src.schemas.vocalizacao_schema import VocalizacaoCreate, VocalizacaoUpdate


class VocalizacaoService:
    async def get_all(self, db: AsyncSession) -> list[Vocalizacao]:
        result = await db.execute(select(Vocalizacao).order_by(Vocalizacao.nome))
        return result.scalars().all()

    async def get_one(self, id: int, db: AsyncSession) -> Vocalizacao:
        return await self.__get_by_id(id, db)

    async def create(
        self, vocalizacao: VocalizacaoCreate, db: AsyncSession, usuario_id: int
    ) -> Vocalizacao:
        query = await db.execute(
            select(Vocalizacao).where(Vocalizacao.nome == vocalizacao.nome)
        )
        vocalizacao_exists = query.scalars().first()
        if vocalizacao_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vocalização já cadastrada.",
            )
        db_vocalizacao = vocalizacao.model_dump()
        db_vocalizacao["id_usuario"] = usuario_id
        db_vocalizacao = Vocalizacao(**db_vocalizacao)
        db.add(db_vocalizacao)
        await db.commit()
        await db.refresh(db_vocalizacao)
        return db_vocalizacao

    async def __get_by_id(self, id: int, db: AsyncSession) -> Vocalizacao:
        result = await db.execute(select(Vocalizacao).where(Vocalizacao.id == id))
        vocalizacao = result.scalars().first()
        if not vocalizacao:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vocalização não encontrada",
            )
        return vocalizacao

    async def update(
        self,
        id: int,
        vocalizacao: VocalizacaoUpdate,
        id_usuario: int,
        role: str,
        db: AsyncSession
    ) -> Vocalizacao:
        vocalizacao_db = await self.get_one(id, db)

        if role != "admin" and vocalizacao_db.id_usuario != id_usuario:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para atualizar esta vocalização.",
            )
        for key, value in vocalizacao.model_dump(exclude_unset=True).items():
            setattr(vocalizacao_db, key, value)

        await db.commit()
        await db.refresh(vocalizacao_db)
        return vocalizacao_db

    async def delete(self, id: int, db: AsyncSession) -> None:
        vocalizacao = await self.__get_by_id(id, db)
        await db.delete(vocalizacao)
        await db.commit()
