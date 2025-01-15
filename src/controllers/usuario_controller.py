from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas.usuario_schema import UsuarioBase, UsuarioCreate, UsuarioResponse
from src.services.usuario_service import UsuarioService

router = APIRouter()
service = UsuarioService()


@router.get("/", response_model=list[UsuarioResponse])
async def get_all(db: AsyncSession = Depends(get_db)):
    return await service.get_all(db)


@router.get("/{id}", response_model=UsuarioResponse or None)
async def get_by_id(id: int, db: AsyncSession = Depends(get_db)):
    return await service.get_one(id, db)


@router.patch("/{id}", response_model=UsuarioResponse)
async def update(id: int, usuario: UsuarioBase, db: AsyncSession = Depends(get_db)):
    return await service.update(id, usuario, db)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(id: int, db: AsyncSession = Depends(get_db)):
    await service.delete(id, db)
