from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas.auth_schema import (
    AuthLogin,
    AuthRegister,
    ConfirmRegistration,
    ResetPassword,
    EmailRequest,
    Token,
)
from src.schemas.usuario_schema import UsuarioResponse
from src.services.auth_service import AuthService

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
    current_token: Token,
    db: AsyncSession = Depends(get_db),
):
    return await service.refresh_token(current_token, db)


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
