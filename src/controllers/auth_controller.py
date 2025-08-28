from fastapi import APIRouter, Depends, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from src.database import get_db
from src.schemas.auth_schema import (
    AuthLogin,
    AuthRegister,
    ConfirmRegistration,
    ResetPassword,
    EmailRequest,
    Token,
    RefreshTokenRequest,
    LogoutRequest,
)
from src.schemas.usuario_schema import UsuarioResponse
from src.services.auth_service import AuthService
from src.security import get_current_user

router = APIRouter()
service = AuthService()


@router.post(
    "/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED
)
async def register(usuario: AuthRegister, db: AsyncSession = Depends(get_db)):
    return await service.register(usuario, db)


@router.post("/login", response_model=Token)
async def login(login: AuthLogin, db: AsyncSession = Depends(get_db)):
    tokens = await service.authenticate(login, db)
    return tokens


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    return await service.refresh_token(refresh_request, db)


@router.post("/password-reset", response_model=dict)
async def request_password_reset(
    request: EmailRequest, db: AsyncSession = Depends(get_db)
):
    await service.request_password_reset(request.email, db)
    return {"detail": "Código de redefinição de senha enviado para o e-mail."}


@router.post("/confirm-password-reset", response_model=dict)
async def confirm_password_reset(
    confirm: ResetPassword, db: AsyncSession = Depends(get_db)
):
    await service.confirm_password_reset(
        confirm.email, confirm.codigo_confirmacao, confirm.nova_senha, db
    )
    return {"detail": "Senha redefinida com sucesso."}


@router.post("/confirm-registration", response_model=dict)
async def confirm_registration(
    confirm: ConfirmRegistration, db: AsyncSession = Depends(get_db)
):
    await service.confirm_registration(confirm.email, confirm.codigo_confirmacao, db)
    return {"detail": "Cadastro confirmado com sucesso."}


@router.post("/resend-confirmation-code", response_model=dict)
async def resend_confirmation_code(
    confirm: EmailRequest, db: AsyncSession = Depends(get_db)
):
    await service.resend_confirmation_code(confirm.email, db)
    return {"detail": "Novo código de confirmação enviado para o e-mail."}


@router.post("/logout", response_model=dict)
async def logout(
    logout_request: LogoutRequest,
    current_user = Depends(get_current_user),
    authorization: Optional[str] = Header(None),
):
    # Extrair o access token do header Authorization
    access_token = None
    if authorization and authorization.startswith("Bearer "):
        access_token = authorization[7:]
    
    return await service.logout(current_user.id, access_token, logout_request.refresh_token)
