from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas.usuario_schema import UsuarioResponse
from src.schemas.vocalizacao_schema import VocalizacaoCreate, VocalizacaoResponse
from src.security import get_current_user, verify_role
from src.services.vocalizacao_service import VocalizacaoService, VocalizacaoUpdate

router = APIRouter()
service = VocalizacaoService()


@router.get(
    "/",
    response_model=list[VocalizacaoResponse],
    dependencies=[Depends(get_current_user)],
)
async def get_all(db: AsyncSession = Depends(get_db)):
    return await service.get_all(db)


@router.get(
    "/{id}",
    response_model=VocalizacaoResponse,
    dependencies=[Depends(get_current_user)],
)
async def get_by_id(id: int, db: AsyncSession = Depends(get_db)):
    return await service.get_one(id, db)


@router.post(
    "/",
    response_model=VocalizacaoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create(
    vocalizacao: VocalizacaoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioResponse = Depends(get_current_user),
):
    usuario_id = current_user.id
    return await service.create(vocalizacao, db, usuario_id)


@router.patch(
    "/{id}",
    response_model=VocalizacaoResponse,
)
async def update(
    id: int,
    vocalizacao: VocalizacaoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioResponse = Depends(get_current_user),
):
    return await service.update(id, vocalizacao, current_user.id, current_user.role, db)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_role("admin"))],
)
async def delete(id: int, db: AsyncSession = Depends(get_db)):
    await service.delete(id, db)
