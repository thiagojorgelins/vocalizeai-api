from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models import Vocalizacao, Audio
import os
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError, NoCredentialsError
from src.schemas.vocalizacao_schema import VocalizacaoCreate, VocalizacaoUpdate


class VocalizacaoService:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_DEFAULT_REGION"),
            config=Config(signature_version="s3v4"),
        )
        self.bucket_name = os.getenv("S3_BUCKET_NAME")

    def _list_s3_objects(self, prefix):
        """Lista objetos no S3 com o prefixo especificado"""
        try:
            print(f"Buscando objetos com prefixo: {prefix}")
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name, Prefix=prefix
            )

            objects = []
            if "Contents" in response:
                objects = [obj["Key"] for obj in response["Contents"]]
                print(f"Encontrados {len(objects)} objetos: {objects}")
            else:
                print(f"Nenhum objeto encontrado com prefixo '{prefix}'")

            return objects
        except Exception as e:
            print(f"Erro ao listar objetos no S3: {str(e)}")
            return []

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

    async def _get_audio_by_vocalizacao(
        self, id_vocalizacao: int, db: AsyncSession
    ) -> list[Audio]:
        result = await db.execute(
            select(Audio).where(Audio.id_vocalizacao == id_vocalizacao)
        )
        return result.scalars().all()

    def _rename_s3_object(self, old_key, new_key):
        try:
            print(f"Renomeando objeto de '{old_key}' para '{new_key}'")

            self.s3_client.copy_object(
                Bucket=self.bucket_name,
                CopySource=f"{self.bucket_name}/{old_key}",
                Key=new_key,
            )

            self.s3_client.delete_object(Bucket=self.bucket_name, Key=old_key)

            print(f"Objeto renomeado com sucesso")
            return True
        except Exception as e:
            print(f"Erro ao renomear objeto: {str(e)}")
            return False

    async def update(
        self,
        id: int,
        vocalizacao: VocalizacaoUpdate,
        id_usuario: int,
        role: str,
        db: AsyncSession,
    ) -> Vocalizacao:
        vocalizacao_db = await self.get_one(id, db)

        if role != "admin" and vocalizacao_db.id_usuario != id_usuario:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para atualizar esta vocalização.",
            )

        nome_antigo = vocalizacao_db.nome
        dados_atualizacao = vocalizacao.model_dump(exclude_unset=True)

        if "nome" in dados_atualizacao and dados_atualizacao["nome"] != nome_antigo:
            print(
                f"Atualizando nome da vocalização de '{nome_antigo}' para '{dados_atualizacao['nome']}'"
            )

            audios = await self._get_audio_by_vocalizacao(id, db)

            for audio in audios:
                old_filename = audio.nome_arquivo
                nome_novo = dados_atualizacao["nome"].lower()

                if old_filename.lower().startswith(nome_antigo.lower()):
                    new_filename = old_filename.replace(
                        nome_antigo.lower(), nome_novo, 1
                    )
                    print(
                        f"Renomeando arquivo principal: {old_filename} -> {new_filename}"
                    )

                    rename_success = self._rename_s3_object(old_filename, new_filename)

                    if rename_success:
                        audio.nome_arquivo = new_filename
                        await db.commit()

                        base_old = old_filename[:-4]
                        base_new = new_filename[:-4]

                        segment_prefix = f"{base_old}_segment_"
                        segment_files = self._list_s3_objects(segment_prefix)

                        for segment in segment_files:
                            new_segment = segment.replace(base_old, base_new, 1)
                            self._rename_s3_object(segment, new_segment)

        for key, value in dados_atualizacao.items():
            setattr(vocalizacao_db, key, value)

        await db.commit()
        await db.refresh(vocalizacao_db)
        return vocalizacao_db

    async def delete(self, id: int, db: AsyncSession) -> None:
        vocalizacao = await self.__get_by_id(id, db)

        audios = await self._get_audio_by_vocalizacao(id, db)

        for audio in audios:
            try:
                print(f"Deletando arquivo principal: {audio.nome_arquivo}")
                self.s3_client.delete_object(
                    Bucket=self.bucket_name, Key=audio.nome_arquivo
                )

                base_filename = audio.nome_arquivo[:-4]
                segment_prefix = f"{base_filename}_segment_"

                segment_files = self._list_s3_objects(segment_prefix)

                for segment in segment_files:
                    print(f"Deletando segmento: {segment}")
                    self.s3_client.delete_object(Bucket=self.bucket_name, Key=segment)

                await db.delete(audio)

            except (NoCredentialsError, ClientError) as e:
                print(f"Erro ao deletar arquivo no S3: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Erro ao deletar arquivo no S3: {str(e)}",
                )

        await db.delete(vocalizacao)
        await db.commit()
