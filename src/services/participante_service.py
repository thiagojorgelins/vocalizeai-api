from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models import Participante
from src.schemas.participante_schema import ParticipanteCreate, ParticipanteUpdate


class ParticipanteService:

    async def get_all(self, db: AsyncSession) -> list[Participante]:
        result = await db.execute(select(Participante))
        return result.scalars().all()

    async def get_one(self, id: int, db: AsyncSession) -> Participante:
        result = await db.execute(select(Participante).where(Participante.id == id))
        participante = result.scalars().first()
        if not participante:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Participante não encontrado",
            )
        return participante

    async def create(
        self, participante: ParticipanteCreate, usuario_id: int, db: AsyncSession
    ) -> Participante:
        result = await db.execute(
            select(Participante).where(Participante.usuario_id == usuario_id)
        )
        existing_participante = result.scalars().first()
        if existing_participante:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O usuário já possui um participante associado.",
            )
        participante_data = participante.model_dump()
        participante_data["usuario_id"] = usuario_id

        db_participante = Participante(**participante_data)
        db.add(db_participante)
        await db.commit()
        await db.refresh(db_participante)
        return db_participante

    async def update(
        self, id: int, participante: ParticipanteUpdate, db: AsyncSession
    ) -> Participante:
        participante_db = await self.get_one(id, db)
        participante_db.nivel_suporte = participante.nivel_suporte
        participante_db.genero = participante.genero
        participante_db.condicao = participante.condicao
        participante_db.idade = participante.idade
        participante_db.qtd_palavras = participante.qtd_palavras

        await db.commit()
        await db.refresh(participante_db)
        return participante_db

    async def delete(self, id: int, db: AsyncSession) -> None:
        participante = await self.get_one(id, db)
        await db.delete(participante)
        await db.commit()
