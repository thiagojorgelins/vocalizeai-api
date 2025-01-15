from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from src.models import Vocalizacao
from src.schemas.vocalizacao_schema import VocalizacaoCreate


class VocalizacaoService:
    async def get_all(self, db: AsyncSession) -> list[Vocalizacao]:
        result = await db.execute(select(Vocalizacao))
        return result.scalars().all()

    async def get_one(self, id: int, db: AsyncSession) -> Vocalizacao:
        return await self.__get_by_id(id, db)

    async def create(
        self, vocalizacao: VocalizacaoCreate, db: AsyncSession
    ) -> Vocalizacao:
        db_vocalizacao = Vocalizacao(**vocalizacao.model_dump())
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
        self, id: int, vocalizacao: VocalizacaoCreate, db: AsyncSession
    ) -> Vocalizacao:
        vocalizacao_db = await self.__get_by_id(id, db)
        vocalizacao_db.nome = vocalizacao.nome
        vocalizacao_db.descricao = vocalizacao.descricao
        await db.commit()
        await db.refresh(vocalizacao_db)
        return vocalizacao_db

    async def delete(self, id: int, db: AsyncSession) -> None:
        vocalizacao = await self.__get_by_id(id, db)
        await db.delete(vocalizacao)
        await db.commit()
