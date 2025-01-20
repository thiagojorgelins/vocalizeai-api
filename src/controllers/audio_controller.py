from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.usuario_schema import UsuarioResponse
from src.models.usuario_model import Usuario
from src.security import get_current_user, verify_role
from src.database import get_db
from src.schemas.audio_schema import AudioResponse
from src.services.audio_service import AudioService

router = APIRouter()
service = AudioService()


@router.post(
    "/",
    response_model=AudioResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_audio(
    id_vocalizacao: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioResponse = Depends(get_current_user),
):
    if not file.content_type.startswith("audio"):
        raise HTTPException(
            status_code=400, detail="Arquivo de áudio inválido")

    file_data = await file.read()

    return await service.upload_audio(
        id_vocalizacao=id_vocalizacao,
        file_data=file_data,
        current_user=current_user,
        file_name=file.filename,
        db=db,
    )


@router.post(
    "/bulk",
    response_model=list[AudioResponse],
    status_code=status.HTTP_201_CREATED,
)
async def upload_varios_audios(
    id_vocalizacao: int,
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    for file in files:
        if not file.content_type.startswith("audio"):
            raise HTTPException(
                status_code=400, detail="Um ou mais arquivos são inválidos"
            )

    file_datas = [await file.read() for file in files]

    return await service.upload_multiple_audios(
        id_vocalizacao=id_vocalizacao,
        files_data=file_datas,
        file_names=[file.filename for file in files],
        current_user=current_user,
        db=db,
    )


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
