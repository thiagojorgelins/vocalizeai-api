import os
from tempfile import NamedTemporaryFile

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Audio, Participante
from src.schemas.participante_schema import ParticipanteCreate, ParticipanteUpdate
from src.services.audio_service import AudioService


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
            select(Participante).where(Participante.id_usuario == usuario_id)
        )
        existing_participante = result.scalars().first()
        if existing_participante:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O usuário já possui um participante associado.",
            )
        participante_data = participante.model_dump()
        participante_data["id_usuario"] = usuario_id
        db_participante = Participante(**participante_data)
        db.add(db_participante)
        await db.commit()
        await db.refresh(db_participante)
        return db_participante

    async def update(
        self,
        id: int,
        participante: ParticipanteUpdate,
        usuario_id: int,
        role: str,
        db: AsyncSession,
    ) -> Participante:
        participante_db = await self.get_one(id, db)

        if role != "admin" and participante_db.id_usuario != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para atualizar este participante",
            )

        for key, value in participante.model_dump(exclude_unset=True).items():
            setattr(participante_db, key, value)

        await db.commit()
        await db.refresh(participante_db)
        return participante_db

    async def delete(self, id: int, db: AsyncSession) -> None:
        participante = await self.get_one(id, db)

        result = await db.execute(select(Audio).where(Audio.id_participante == id))
        audios = result.scalars().all()

        if audios:
            audio_service = AudioService()
            for audio in audios:
                await audio_service.delete_audio(audio.id, db)

        await db.delete(participante)
        await db.commit()
