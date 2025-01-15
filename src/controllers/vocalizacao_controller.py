from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas.vocalizacao_schema import VocalizacaoCreate, VocalizacaoResponse
from src.security import get_current_user
from src.services.vocalizacao_service import VocalizacaoService

router = APIRouter()
service = VocalizacaoService()


@router.get("/", response_model=list[VocalizacaoResponse])
async def get_all(db: AsyncSession = Depends(get_db)):
    return await service.get_all(db)


@router.get("/{id}", response_model=VocalizacaoResponse)
async def get_by_id(id: int, db: AsyncSession = Depends(get_db)):
    return await service.get_one(id, db)


@router.post(
    "/", response_model=VocalizacaoResponse, status_code=status.HTTP_201_CREATED
)
async def create(vocalizacao: VocalizacaoCreate, db: AsyncSession = Depends(get_db)):
    return await service.create(vocalizacao, db)


@router.patch("/{id}", response_model=VocalizacaoResponse)
async def update(
    id: int, vocalizacao: VocalizacaoCreate, db: AsyncSession = Depends(get_db)
):
    return await service.update(id, vocalizacao, db)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(id: int, db: AsyncSession = Depends(get_db)):
    await service.delete(id, db)
