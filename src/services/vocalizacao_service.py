from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
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
        query = await db.execute(
            select(Vocalizacao).where(Vocalizacao.nome == vocalizacao.nome)
        )
        vocalizacao_exists = query.scalars().first()
        if vocalizacao_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vocalização já cadastrada.",
            )
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
        for key, value in vocalizacao.model_dump(exclude_unset=True).items():
            setattr(vocalizacao_db, key, value)

        await db.commit()
        await db.refresh(vocalizacao_db)
        return vocalizacao_db

    async def delete(self, id: int, db: AsyncSession) -> None:
        vocalizacao = await self.__get_by_id(id, db)
        await db.delete(vocalizacao)
        await db.commit()
