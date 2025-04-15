from datetime import datetime
import os
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models.participante_model import Participante
from src.preprocessing.preprocessing import AudioSegment
from src.schemas.audio_schema import AudioResponse
from src.schemas.usuario_schema import UsuarioResponse
from src.security import get_current_user, verify_role
from src.services.audio_service import AudioService

router = APIRouter()
service = AudioService()


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=AudioResponse,
)
async def audio_upload(
    id_vocalizacao: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if not file.content_type.startswith("audio"):
        raise HTTPException(status_code=400, detail="Arquivo de áudio inválido.")

    with NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav_file:
        temp_wav_path = temp_wav_file.name

    try:
        audio = AudioSegment.from_file(file.file)
        audio.export(temp_wav_path, format="wav")

        # Salvar áudio original
        with open(temp_wav_path, "rb") as audio_file:
            file_data = audio_file.read()

        audio_record = await service.upload_audio(
            id_vocalizacao=id_vocalizacao,
            file_data=file_data,
            current_user=current_user,
            db=db,
            original_filename=file.filename,
        )

        return audio_record
    finally:
        os.remove(temp_wav_path)


@router.get("/{id}/play")
async def get_audio_url(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioResponse = Depends(get_current_user),
):
    """
    Retorna a URL de um áudio específico do S3 para poder reproduzi-lo.
    Verifica o cabeçalho 'x-environment' para decidir qual bucket usar.
    """
    audio_db = await service._get_one(id, db)

    if current_user.role != "admin" and current_user.id != audio_db.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para acessar esse áudio.",
        )
    presigned_url = service.generate_presigned_url(
        bucket_name=os.getenv("S3_BUCKET_NAME"), object_name=audio_db.nome_arquivo
    )

    return {"url": presigned_url}


@router.patch(
    "/{id}",
    response_model=AudioResponse,
    dependencies=[Depends(verify_role("admin"))],
)
async def update(
    id: int,
    audio_data: dict,
    db: AsyncSession = Depends(get_db),
):
    """
    Atualiza um áudio específico, incluindo a possibilidade de alterar a vocalização
    e renomear o arquivo no S3 de acordo com o novo rótulo
    """
    audio_db = await service._get_one(id, db)

    if (
        "id_vocalizacao" in audio_data
        and audio_data["id_vocalizacao"] != audio_db.id_vocalizacao
    ):
        vocalizacao = await service._get_vocalizacao(audio_data["id_vocalizacao"], db)
        participante = await service._get_participante(audio_db.id_participante, db)

        parts = audio_db.nome_arquivo.split("_")
        timestamp_parts = []
        for part in parts:
            if part.count("-") >= 4:
                timestamp_parts.append(part)

        timestamp = (
            timestamp_parts[0]
            if timestamp_parts
            else datetime.now().strftime("%Y-%m-%d-%H-%M")
        )

        novo_nome_arquivo = service._generate_filename(
            vocalizacao_nome=vocalizacao.nome,
            audio_id=audio_db.id,
            participante_id=participante.id,
            timestamp_str=timestamp,
        )

        try:
            service.s3_client.copy_object(
                Bucket=os.getenv("S3_BUCKET_NAME"),
                CopySource=f"{os.getenv('S3_BUCKET_NAME')}/{audio_db.nome_arquivo}",
                Key=novo_nome_arquivo,
            )

            service.s3_client.delete_object(
                Bucket=os.getenv("S3_BUCKET_NAME"), Key=audio_db.nome_arquivo
            )

            audio_data["nome_arquivo"] = novo_nome_arquivo

            if hasattr(audio_db, "segments") and audio_db.segments:
                base_old_filename = audio_db.nome_arquivo[:-4]
                base_new_filename = novo_nome_arquivo[:-4]

                updated_segments = []

                for segment_name in audio_db.segments:
                    segment_number = segment_name.split("_segment_")[-1]
                    novo_segment_name = f"{base_new_filename}_segment_{segment_number}"

                    service.s3_client.copy_object(
                        Bucket=os.getenv("S3_BUCKET_NAME"),
                        CopySource=f"{os.getenv('S3_BUCKET_NAME')}/{segment_name}",
                        Key=novo_segment_name,
                    )

                    service.s3_client.delete_object(
                        Bucket=os.getenv("S3_BUCKET_NAME"), Key=segment_name
                    )

                    updated_segments.append(novo_segment_name)

                audio_data["segments"] = updated_segments
            else:
                try:
                    base_old_filename = audio_db.nome_arquivo[:-4]
                    base_new_filename = novo_nome_arquivo[:-4]

                    response = service.s3_client.list_objects_v2(
                        Bucket=os.getenv("S3_BUCKET_NAME"),
                        Prefix=f"{base_old_filename}_segment_",
                    )

                    updated_segments = []

                    if "Contents" in response:
                        for obj in response["Contents"]:
                            old_key = obj["Key"]
                            segment_number = old_key.split("_segment_")[-1]
                            novo_segment_name = (
                                f"{base_new_filename}_segment_{segment_number}"
                            )

                            service.s3_client.copy_object(
                                Bucket=os.getenv("S3_BUCKET_NAME"),
                                CopySource=f"{os.getenv('S3_BUCKET_NAME')}/{old_key}",
                                Key=novo_segment_name,
                            )

                            service.s3_client.delete_object(
                                Bucket=os.getenv("S3_BUCKET_NAME"), Key=old_key
                            )

                            updated_segments.append(novo_segment_name)

                        audio_data["segments"] = updated_segments

                except Exception as e:
                    print(f"Erro ao processar segmentos: {str(e)}")

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao renomear arquivo no S3: {str(e)}",
            )

    return await service.update(id, audio_data, db)


@router.delete(
    "/{id}",
    dependencies=[Depends(verify_role("admin"))],
)
async def delete(id: int, db: AsyncSession = Depends(get_db)):
    await service.delete_audio(id, db)
    return {"message": "Áudio deletado com sucesso"}


@router.delete(
    "/usuario/{id_usuario}",
    dependencies=[Depends(verify_role("admin"))],
)
async def delete_audios_by_user(id_usuario: int, db: AsyncSession = Depends(get_db)):
    """Endpoint para deletar todos os áudios associados a um usuário específico"""
    await service.delete_all_audios_by_user(id_usuario, db)
    return {"message": "Todos os áudios do usuário foram deletados com sucesso"}


@router.get(
    "/usuario/{id_usuario}",
    response_model=list[AudioResponse],
    dependencies=[Depends(verify_role("admin"))],
)
async def list_audios_by_user(
    id_usuario: int,
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioResponse = Depends(get_current_user),
):
    """Endpoint para listar todos os áudios associados a um usuário específico"""
    if current_user.role != "admin" and current_user.id != id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para acessar esses áudios",
        )

    return await service.list_audios_by_user(id_usuario, db)
