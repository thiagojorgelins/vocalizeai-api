import asyncio
import base64
import os
from email.mime.text import MIMEText

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from pydantic import EmailStr

GMAIL_CLIENT_ID = os.getenv("GMAIL_CLIENT_ID")
GMAIL_CLIENT_SECRET = os.getenv("GMAIL_CLIENT_SECRET")
GMAIL_REFRESH_TOKEN = os.getenv("GMAIL_REFRESH_TOKEN")
GMAIL_SENDER_EMAIL = os.getenv("GMAIL_SENDER_EMAIL")


def build_gmail_service():
    creds = Credentials(
        None,
        refresh_token=GMAIL_REFRESH_TOKEN,
        client_id=GMAIL_CLIENT_ID,
        client_secret=GMAIL_CLIENT_SECRET,
        token_uri="https://oauth2.googleapis.com/token",
    )
    return build("gmail", "v1", credentials=creds)


def create_message(to_email: str, subject: str, html_content: str):
    sender_name = os.getenv("GMAIL_SENDER_NAME")
    message = MIMEText(html_content, "html")
    message["to"] = to_email
    message["from"] = f"{sender_name} <{GMAIL_SENDER_EMAIL}>"
    message["subject"] = subject
    return {"raw": base64.urlsafe_b64encode(message.as_bytes()).decode()}



async def send_email(to_email: EmailStr, subject: str, html_content: str):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _send_email_sync, to_email, subject, html_content)


def _send_email_sync(to_email: str, subject: str, html_content: str):
    try:
        service = build_gmail_service()
        message = create_message(to_email, subject, html_content)
        service.users().messages().send(userId="me", body=message).execute()
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
