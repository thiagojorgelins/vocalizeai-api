import asyncio
import os
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.preprocessing.preprocessing import AudioSegment, segment_data
from src.schemas.audio_schema import AudioResponse
from src.security import get_current_user, verify_role
from src.services.audio_service import AudioService

router = APIRouter()
service = AudioService()


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
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
            audio_bytes = audio_file.read()
            original_audio = await service.upload_audio(
                id_vocalizacao=id_vocalizacao,
                file_data=audio_bytes,
                current_user=current_user,
                db=db,
                is_segment=False
            )

        segments_info = await asyncio.to_thread(segment_data, temp_wav_path)

        if not segments_info:
            raise HTTPException(
                status_code=400, detail="Nenhum segmento válido encontrado."
            )

        saved_data = [original_audio]
        for i, segment in enumerate(segments_info):
            segment_audio = segment["segment_data"]
            segment_bytes = segment_audio.export(format="wav").read()

            audio_data = await service.upload_audio(
                id_vocalizacao=id_vocalizacao,
                file_data=segment_bytes,
                current_user=current_user,
                db=db,
                is_segment=True,
                original_filename=original_audio.nome_arquivo,
                segment_number=i+1
            )
            saved_data.append(audio_data)

        return {"message": "Áudio processado com sucesso.", "segments": saved_data}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar o áudio: {str(e)}"
        )

    finally:
        if os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)

@router.get(
    "/", response_model=list[AudioResponse], dependencies=[Depends(get_current_user)]
)
async def list_audios(db: AsyncSession = Depends(get_db)):
    return await service.list_audios(db)


@router.patch(
    "/{id}",
    response_model=AudioResponse,
    dependencies=[Depends(verify_role("admin"))],
)
async def update(
    id: int,
    audio: AudioResponse,
    db: AsyncSession = Depends(get_db),
):
    return await service.update(id, audio, db)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_user)],
)
async def delete_audio(id: int, db: AsyncSession = Depends(get_db)):
    await service.delete_audio(id, db)
