from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas.participante_schema import (
    ParticipanteCreate,
    ParticipanteResponse,
    ParticipanteUpdate,
)
from src.security import get_current_user
from src.services.participante_service import ParticipanteService

router = APIRouter()
service = ParticipanteService()


@router.get(
    "/",
    response_model=list[ParticipanteResponse],
    dependencies=[Depends(get_current_user)],
)
async def get_all(db: AsyncSession = Depends(get_db)):
    return await service.get_all(db)


@router.get("/{id}", response_model=ParticipanteResponse)
async def get_by_id(id: int, db: AsyncSession = Depends(get_db)):
    return await service.get_one(id, db)


@router.post(
    "/", response_model=ParticipanteResponse, status_code=status.HTTP_201_CREATED
)
async def create(
    participante: ParticipanteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    usuario_id = int(current_user["sub"])
    return await service.create(participante, usuario_id, db)


@router.patch("/{id}", response_model=ParticipanteResponse)
async def update(
    id: int, participante: ParticipanteUpdate, db: AsyncSession = Depends(get_db)
):
    return await service.update(id, participante, db)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(id: int, db: AsyncSession = Depends(get_db)):
    await service.delete(id, db)
