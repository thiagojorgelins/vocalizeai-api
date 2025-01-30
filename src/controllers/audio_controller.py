import os
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.preprocessing.preprocessing import AudioSegment
from src.schemas.audio_schema import AudioResponse
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
    return await service.update(id, audio.dict(), db)


@router.delete(
    "/{id}",
    dependencies=[Depends(verify_role("admin"))],
)
async def delete(id: int, db: AsyncSession = Depends(get_db)):
    await service.delete_audio(id, db)
    return {"message": "Áudio deletado com sucesso"}