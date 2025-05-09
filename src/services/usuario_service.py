import re

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.models import Usuario, Audio, Participante
from src.schemas.usuario_schema import UsuarioUpdate
from src.services.auth_service import AuthService
from src.services.audio_service import AudioService


class UsuarioService:
    async def get_all(self, db: AsyncSession) -> list[Usuario]:
        result = await db.execute(select(Usuario))
        return result.scalars().all()

    async def get_one(self, id: int, db: AsyncSession) -> Usuario:
        return await self.__get_by_id(id, db)

    async def __get_by_id(self, id: int, db: AsyncSession) -> Usuario:
        result = await db.execute(
            select(Usuario)
            .options(joinedload(Usuario.participantes))
            .where(Usuario.id == id)
        )
        usuario = result.scalars().first()
        if usuario is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado.",
            )
        return usuario

    def _validar_email(self, email: str) -> bool:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    async def update(self, id: int, usuario: UsuarioUpdate, db: AsyncSession) -> dict:
        usuario_db = await self.__get_by_id(id, db)

        email_alterado = False
        novo_email = None

        dados_atualizados = usuario.model_dump(exclude_unset=True)

        if "email" in dados_atualizados:
            novo_email = dados_atualizados["email"]

            if not self._validar_email(novo_email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Formato de email inválido.",
                )

            if novo_email != usuario_db.email:
                email_alterado = True

                auth_service = AuthService()
                email_existente = await auth_service.get_by_email(novo_email, db)
                if email_existente:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Este email já está em uso por outra conta.",
                    )

        for key, value in dados_atualizados.items():
            setattr(usuario_db, key, value)

        if email_alterado:
            usuario_db.verificado = False

        await db.commit()
        await db.refresh(usuario_db)

        return {
            "email_alterado": email_alterado,
            "novo_email": novo_email if email_alterado else None,
            "id": usuario_db.id,
            "nome": usuario_db.nome,
            "email": usuario_db.email,
            "celular": usuario_db.celular,
            "verificado": usuario_db.verificado,
            "role": usuario_db.role,
        }

    async def delete(self, id: int, db: AsyncSession) -> None:
        usuario = await self.__get_by_id(id, db)

        result = await db.execute(
            select(Participante).where(Participante.id_usuario == id)
        )
        participante = result.scalars().first()

        if participante:
            result = await db.execute(
                select(Audio).where(Audio.id_participante == participante.id)
            )
            audios = result.scalars().all()

            if audios:
                audio_service = AudioService()
                for audio in audios:
                    await audio_service.delete_audio(audio.id, db)

        result = await db.execute(select(Audio).where(Audio.id_usuario == id))
        audios = result.scalars().all()

        if audios:
            audio_service = AudioService()
            for audio in audios:
                await audio_service.delete_audio(audio.id, db)

        await db.delete(usuario)
        await db.commit()
