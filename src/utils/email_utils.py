import asyncio
import os

import sib_api_v3_sdk
from pydantic import EmailStr
from sib_api_v3_sdk.rest import ApiException

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
BREVO_SENDER_EMAIL = os.getenv("BREVO_SENDER_EMAIL")
BREVO_SENDER_NAME = os.getenv("BREVO_SENDER_NAME")


async def send_email(to_email: EmailStr, subject: str, html_content: str):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _send_email_sync, to_email, subject, html_content)


def _send_email_sync(to_email: str, subject: str, html_content: str):
    try:
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = BREVO_API_KEY

        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration))

        sender = {"name": BREVO_SENDER_NAME, "email": BREVO_SENDER_EMAIL}

        to = [{"email": to_email}]

        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=to,
            html_content=html_content,
            sender=sender,
            subject=subject
        )

        api_response = api_instance.send_transac_email(send_smtp_email)

    except ApiException as e:
        raise Exception(f"Erro ao enviar email: {str(e)}")
    except Exception as e:
        raise Exception(f"Erro ao enviar email: {str(e)}")


async def send_confirmation_email(email: EmailStr, code: str):
    html = f"""
        <h2>Confirmação de Cadastro</h2>
        <p>Seu código de confirmação é: <b>{code}</b></p>
        <p>Código válido por 15 minutos.</p>
    """
    await send_email(email, "Confirmação de Cadastro", html)


async def send_password_reset_email(email: EmailStr, code: str):
    html = f"""
        <h2>Redefinição de Senha</h2>
        <p>Seu código de redefinição de senha é: <b>{code}</b></p>
        <p>Código válido por 15 minutos.</p>
    """
    await send_email(email, "Redefinição de Senha", html)
