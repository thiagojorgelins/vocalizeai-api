import os
from datetime import datetime
from tempfile import NamedTemporaryFile

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Audio, Usuario, Vocalizacao
from src.models.participante_model import Participante
from src.schemas.usuario_schema import UsuarioResponse
from src.preprocessing.preprocessing import segment_data

S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION")

class AudioService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_DEFAULT_REGION
        )

    def _generate_filename(
        self,
        vocalizacao_nome: str,
        audio_id: int,
        participante_id: int,
        is_segment: bool = False,
        original_filename: str = None,
        segment_number: int = None,
        base_filename: str = None,
    ) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")

        if is_segment and base_filename:
            return f"{base_filename}_segment_{segment_number}.wav"

        return (
            f"{vocalizacao_nome.lower()}_{audio_id}_{participante_id}_{timestamp}.wav"
        )

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
        db: AsyncSession,
        original_filename: str,
    ) -> Audio:
        participante = await db.execute(
            select(Participante).where(Participante.id_usuario == current_user.id)
        )
        participante = participante.scalars().first()
        if not participante:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Participante associado ao usuário não encontrado.",
            )

        vocalizacao = await self._get_vocalizacao(id_vocalizacao, db)

        # Criando o registro do áudio no banco para obter o ID
        audio_data = Audio(
            nome_arquivo="temp",
            id_vocalizacao=id_vocalizacao,
            id_usuario=current_user.id,
            id_participante=participante.id,
        )
        db.add(audio_data)
        await db.commit()
        await db.refresh(audio_data)

        # Gerando o nome do arquivo com o ID do áudio
        novo_nome_arquivo = self._generate_filename(
            vocalizacao_nome=vocalizacao.nome,
            audio_id=audio_data.id,
            participante_id=participante.id,
            original_filename=original_filename,
        )

        try:
            # Upload do áudio original
            self.s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=novo_nome_arquivo,
                Body=file_data,
                ContentType='audio/wav'
            )

            # Processar o áudio para obter os segmentos
            with NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav_file:
                temp_wav_file.write(file_data)
                temp_wav_path = temp_wav_file.name

            segments = segment_data(temp_wav_path)

            # Upload dos segmentos
            base_filename = novo_nome_arquivo[:-4]  # Remover a extensão .wav
            for idx, segment_info in enumerate(segments):
                segment_filename = self._generate_filename(
                    vocalizacao_nome=vocalizacao.nome,
                    audio_id=audio_data.id,
                    participante_id=participante.id,
                    is_segment=True,
                    segment_number=idx + 1,
                    base_filename=base_filename,
                )
                segment_data_bytes = segment_info["segment_data"].export(format="wav").read()
                self.s3_client.put_object(
                    Bucket=S3_BUCKET_NAME,
                    Key=segment_filename,
                    Body=segment_data_bytes,
                    ContentType='audio/wav'
                )

        except (NoCredentialsError, ClientError) as e:
            await db.delete(audio_data)
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao salvar o arquivo no S3: {str(e)}",
            )
        finally:
            os.remove(temp_wav_path)

        # Atualizando o nome do arquivo no registro
        audio_data.nome_arquivo = novo_nome_arquivo
        await db.commit()
        await db.refresh(audio_data)

        return audio_data

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

        try:
            self.s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=audio.nome_arquivo)
        except (NoCredentialsError, ClientError) as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao deletar o arquivo no S3: {str(e)}",
            )

        await db.execute(delete(Audio).where(Audio.id == audio_id))
        await db.commit()