import os

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from pydantic import EmailStr

config = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT")),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

mail = FastMail(config=config)


async def send_confirmation_email(email: EmailStr, code: str):
    message = MessageSchema(
        subject="Confirmação de Cadastro",
        recipients=[email],
        body=f"""
          Seu código de confirmação é: <b>{code}</b>
          <br>
          Código válido por 15 minutos.
        """,
        subtype="html",
    )
    await mail.send_message(message)


async def send_password_reset_email(email: EmailStr, code: str):
    message = MessageSchema(
        subject="Redefinição de Senha",
        recipients=[email],
        body=f'''
          Seu código de redefinição de senha é: <b>{code}</b>
          <br>
          Código válido por 15 minutos.
        ''',
        subtype="html",
    )
    await mail.send_message(message)
