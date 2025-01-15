from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas.audio_schema import AudioCreate, AudioResponse
from src.services.audio_service import AudioService

router = APIRouter()
audio_service = AudioService()


@router.post("/", response_model=AudioResponse, status_code=status.HTTP_201_CREATED)
async def upload_audio(
    id_usuario: int,
    id_vocalizacao: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    if not file.content_type.startswith("audio"):
        raise HTTPException(status_code=400, detail="Arquivo de áudio inválido")

    file_data = await file.read()
    audio_data = AudioCreate(
        nome_arquivo=file.filename,
        id_vocalizacao=id_vocalizacao,
        id_usuario=id_usuario,
    )
    return await audio_service.upload_audio(audio_data, file_data, db)


@router.post(
    "/bulk", response_model=list[AudioResponse], status_code=status.HTTP_201_CREATED
)
async def upload_varios_audios(
    id_usuario: int,
    id_vocalizacao: int,
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
):
    for file in files:
        if not file.content_type.startswith("audio"):
            raise HTTPException(
                status_code=400, detail="Um ou mais arquivos são inválidos"
            )

    file_datas = [await file.read() for file in files]
    audio_datas = [
        AudioCreate(
            nome_arquivo=file.filename,
            id_vocalizacao=id_vocalizacao,
            id_usuario=id_usuario,
        )
        for file in files
    ]
    return await audio_service.upload_multiple_audios(audio_datas, file_datas, db)


@router.get("/", response_model=list[AudioResponse])
async def list_audios(db: AsyncSession = Depends(get_db)):
    return await audio_service.list_audios(db)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_audio(id: int, db: AsyncSession = Depends(get_db)):
    await audio_service.delete_audio(id, db)
