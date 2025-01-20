from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.usuario_schema import UsuarioResponse
from src.database import get_db
from src.schemas.participante_schema import (
    ParticipanteCreate,
    ParticipanteResponse,
    ParticipanteUpdate,
)
from src.security import get_current_user, verify_role
from src.services.participante_service import ParticipanteService

router = APIRouter()
service = ParticipanteService()


@router.get(
    "/",
    response_model=list[ParticipanteResponse],
    dependencies=[Depends(verify_role("admin"))],
)
async def get_all(db: AsyncSession = Depends(get_db)):
    return await service.get_all(db)


@router.get(
    "/{id}",
    response_model=ParticipanteResponse,
    dependencies=[Depends(get_current_user)],
)
async def get_by_id(id: int, db: AsyncSession = Depends(get_db)):
    return await service.get_one(id, db)


@router.post(
    "/", response_model=ParticipanteResponse, status_code=status.HTTP_201_CREATED
)
async def create(
    participante: ParticipanteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioResponse = Depends(get_current_user),
):
    usuario_id = current_user.id
    return await service.create(participante, usuario_id, db)


@router.patch(
    "/{id}",
    response_model=ParticipanteResponse,
)
async def update(
    id: int, participante: ParticipanteUpdate, db: AsyncSession = Depends(get_db), current_user: UsuarioResponse = Depends(get_current_user)
):
    if current_user.role == "admin" or current_user.id == id:
        return await service.update(id, participante, db)
    else:
        raise HTTPException(status_code=403, detail="Forbidden")


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_user)],
)
async def delete(id: int, db: AsyncSession = Depends(get_db)):
    await service.delete(id, db)
