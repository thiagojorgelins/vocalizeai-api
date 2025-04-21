from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas.usuario_schema import UsuarioResponse
from src.schemas.vocalizacao_schema import (
    VocalizacaoCreate,
    VocalizacaoResponse,
    VocalizacaoUpdate,
)
from src.security import get_current_user, verify_role
from src.services.vocalizacao_service import VocalizacaoService

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
    try:
        updated = await service.update(
            id, vocalizacao, current_user.id, current_user.role, db
        )
        return updated
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar vocalização: {str(e)}",
        )


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioResponse = Depends(verify_role("admin")),
):
    try:
        if current_user.role == "admin":
            await service.delete(id, db)
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para excluir este participante",
            )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar vocalização: {str(e)}",
        )
