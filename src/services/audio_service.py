import os
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from src.schemas.usuario_schema import UsuarioResponse
from src.models.participante_model import Participante
from src.models import Audio, Usuario, Vocalizacao
from src.schemas.audio_schema import AudioCreate

UPLOAD_DIR = "uploads"


class AudioService:
    def __init__(self):
        if not os.path.exists(UPLOAD_DIR):
            os.makedirs(UPLOAD_DIR)

    async def _get_usuario(self, id_usuario: int, db: AsyncSession) -> Usuario:
        result = await db.execute(select(Usuario).where(Usuario.id == id_usuario))
        usuario = result.scalars().first()
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado."
            )
        return usuario

    async def _get_participante(
        self, id_participante: int, db: AsyncSession
    ) -> Participante:
        result = await db.execute(
            select(Participante).where(Participante.id == id_participante)
        )
        participante = result.scalars().first()
        if not participante:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Participante não encontrado.",
            )
        return participante

    async def _get_vocalizacao(
        self, id_vocalizacao: int, db: AsyncSession
    ) -> Vocalizacao:
        result = await db.execute(
            select(Vocalizacao).where(Vocalizacao.id == id_vocalizacao)
        )
        vocalizacao = result.scalars().first()
        if not vocalizacao:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vocalização não encontrada.",
            )
        return vocalizacao

    async def upload_audio(
        self,
        id_vocalizacao: int,
        file_data: bytes,
        current_user: UsuarioResponse,
        file_name: str,
        db: AsyncSession,
    ) -> Audio:
        participante = await db.execute(
            select(Participante).where(
                Participante.id_usuario == current_user.id)
        )
        participante = participante.scalars().first()
        if not participante:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Participante associado ao usuário não encontrado.",
            )

        vocalizacao = await self._get_vocalizacao(id_vocalizacao, db)

        novo_nome_arquivo = f"{vocalizacao.nome.lower()}_{file_name}"
        file_path = os.path.join(UPLOAD_DIR, novo_nome_arquivo)

        try:
            with open(file_path, "wb") as buffer:
                buffer.write(file_data)
        except IOError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao salvar o arquivo: {str(e)}",
            )

        audio_data = Audio(
            nome_arquivo=novo_nome_arquivo,
            id_vocalizacao=id_vocalizacao,
            id_usuario=current_user.id,
            id_participante=participante.id,
        )
        db.add(audio_data)
        await db.commit()
        await db.refresh(audio_data)
        return audio_data

    async def upload_multiple_audios(
        self,
        id_vocalizacao: int,
        files_data: list[bytes],
        file_names: list[str],
        current_user: Usuario,
        db: AsyncSession,
    ) -> list[Audio]:
        uploaded_audios = []
        try:
            for file_data, file_name in zip(files_data, file_names):
                uploaded_audio = await self.upload_audio(
                    id_vocalizacao=id_vocalizacao,
                    file_data=file_data,
                    current_user=current_user,
                    file_name=file_name,
                    db=db,
                )
                uploaded_audios.append(uploaded_audio)
        except Exception as e:
            for audio in uploaded_audios:
                await self.delete_audio(audio.id, db)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao fazer upload de múltiplos áudios: {str(e)}",
            )
        return uploaded_audios

    async def list_audios(self, db: AsyncSession) -> list[Audio]:
        result = await db.execute(select(Audio))
        return result.scalars().all()

    async def _get_one(self, id: int, db: AsyncSession) -> Audio:
        result = await db.execute(select(Audio).where(Audio.id == id))
        audio = result.scalars().first()
        if not audio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Áudio não encontrado."
            )
        return audio

    async def update(self, id: int, audio_data: dict, db: AsyncSession) -> Audio:
        audio_db = await self._get_one(id, db)
        for key, value in audio_data.items():
            setattr(audio_db, key, value)

        await db.commit()
        await db.refresh(audio_db)
        return audio_db

    async def delete_audio(self, audio_id: int, db: AsyncSession) -> None:
        result = await db.execute(select(Audio).where(Audio.id == audio_id))
        audio = result.scalars().first()
        if not audio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Áudio não encontrado."
            )

        file_path = os.path.join(UPLOAD_DIR, audio.nome_arquivo)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except IOError as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Erro ao deletar o arquivo: {str(e)}",
                )

        await db.execute(delete(Audio).where(Audio.id == audio_id))
        await db.commit()
