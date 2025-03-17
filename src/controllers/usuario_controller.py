from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.security import get_current_user, verify_role
from src.database import get_db
from src.schemas.usuario_schema import UsuarioPayload, UsuarioResponse, UsuarioUpdate
from src.services.usuario_service import UsuarioService
from src.services.auth_service import AuthService

router = APIRouter()
service = UsuarioService()
auth_service = AuthService()


@router.get(
    "/",
    response_model=list[UsuarioResponse],
    dependencies=[Depends(verify_role("admin"))],
)
async def get_all(db: AsyncSession = Depends(get_db)):
    return await service.get_all(db)


@router.get(
    "/{id}",
    response_model=UsuarioPayload or None,
    dependencies=[Depends(get_current_user)],
)
async def get_by_id(id: int, db: AsyncSession = Depends(get_db)):
    return await service.get_one(id, db)


@router.patch("/{id}")
async def update(
    id: int,
    usuario: UsuarioUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioResponse = Depends(get_current_user),
):
    if current_user.role == "admin" or current_user.id == id:
        result = await service.update(id, usuario, db)
        
        if result.get("email_alterado"):
            await auth_service.resend_confirmation_code(result["novo_email"], db)
            return {
                "usuario": {
                    "id": result["id"],
                    "nome": result["nome"],
                    "email": result["email"],
                    "celular": result["celular"],
                    "verificado": result["verificado"],
                    "role": result["role"]
                },
                "detail": "Dados atualizados. Um código de confirmação foi enviado para o novo email.",
                "email_alterado": True
            }
        
        return {
            "usuario": {
                "id": result["id"],
                "nome": result["nome"],
                "email": result["email"],
                "celular": result["celular"],
                "verificado": result["verificado"],
                "role": result["role"]
            },
            "detail": "Dados atualizados com sucesso.",
            "email_alterado": False
        }
    else:
        raise HTTPException(status_code=403, detail="Forbidden")


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_user)],
)
async def delete(id: int, db: AsyncSession = Depends(get_db)):
    await service.delete(id, db)