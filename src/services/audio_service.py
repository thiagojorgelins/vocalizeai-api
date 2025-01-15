import os
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from src.models import Audio, Usuario, Vocalizacao
from src.schemas.audio_schema import AudioCreate

UPLOAD_DIR = "uploads"


class AudioService:

    def __init__(self):
        if not os.path.exists(UPLOAD_DIR):
            os.makedirs(UPLOAD_DIR)

    async def upload_audio(
        self, audio_data: AudioCreate, file_data: bytes, db: AsyncSession
    ) -> Audio:
        result_usuario = await db.execute(
            select(Usuario).where(Usuario.id == audio_data.id_usuario)
        )
        usuario = result_usuario.scalars().first()
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
            )

        result_vocalizacao = await db.execute(
            select(Vocalizacao).where(Vocalizacao.id == audio_data.id_vocalizacao)
        )
        vocalizacao = result_vocalizacao.scalars().first()
        if not vocalizacao:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vocalização não encontrada",
            )

        file_path = os.path.join(UPLOAD_DIR, audio_data.nome_arquivo)
        with open(file_path, "wb") as buffer:
            buffer.write(file_data)

        novo_audio = Audio(**audio_data.model_dump())
        db.add(novo_audio)
        await db.commit()
        await db.refresh(novo_audio)
        return novo_audio

    async def upload_multiple_audios(
        self, audios_data: list[AudioCreate], files_data: list[bytes], db: AsyncSession
    ) -> list[Audio]:
        uploaded_audios = []
        for audio_data, file_data in zip(audios_data, files_data):
            uploaded_audio = await self.upload_audio(audio_data, file_data, db)
            uploaded_audios.append(uploaded_audio)
        return uploaded_audios

    async def list_audios(self, db: AsyncSession) -> list[Audio]:
        result = await db.execute(select(Audio))
        return result.scalars().all()

    async def delete_audio(self, audio_id: int, db: AsyncSession) -> None:
        result = await db.execute(select(Audio).where(Audio.id == audio_id))
        audio = result.scalars().first()
        if not audio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Áudio não encontrado"
            )

        file_path = os.path.join(UPLOAD_DIR, audio.nome_arquivo)
        if os.path.exists(file_path):
            os.remove(file_path)

        await db.execute(delete(Audio).where(Audio.id == audio_id))
        await db.commit()
