from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas.usuario_schema import UsuarioCreate, UsuarioResponse
from src.services.usuario_service import UsuarioService
from src.schemas.auth_schema import Login, Token

router = APIRouter()
service = UsuarioService()


@router.post(
    "/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED
)
async def register(usuario: UsuarioCreate, db: AsyncSession = Depends(get_db)):
    return await service.register(usuario, db)


@router.post("/login", response_model=Token)
async def login(login: Login, db: AsyncSession = Depends(get_db)):
    token = await service.authenticate(login, db)
    return {"access_token": token}
