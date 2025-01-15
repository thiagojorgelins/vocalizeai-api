from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas.usuario_schema import UsuarioResponse
from src.services.auth_service import AuthService
from src.schemas.auth_schema import AuthLogin, AuthRegister, Token

router = APIRouter()
service = AuthService()


@router.post(
    "/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED
)
async def register(usuario: AuthRegister, db: AsyncSession = Depends(get_db)):
    return await service.register(usuario, db)


@router.post("/login", response_model=Token)
async def login(login: AuthLogin, db: AsyncSession = Depends(get_db)):
    token = await service.authenticate(login, db)
    return {"access_token": token}


@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_token: str,
    db: AsyncSession = Depends(get_db),
):
    return await service.refresh_token(current_token, db)
