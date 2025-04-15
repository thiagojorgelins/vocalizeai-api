from sqlalchemy import Boolean, DateTime, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class Usuario(Base):
    __tablename__ = "usuario"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    senha: Mapped[str] = mapped_column(String, nullable=False)
    celular: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False, default="user")
    created_at: Mapped[DateTime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )
    verificado: Mapped[bool] = mapped_column(Boolean, default=False)
    aceite_termos: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=text("false")
    )
    participante: Mapped["Participante"] = relationship(
        back_populates="usuario", uselist=False, cascade="all, delete-orphan"
    )
    classificacoes: Mapped[list["Classificacao"]] = relationship(
        back_populates="usuario"
    )
    audios: Mapped[list["Audio"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan"
    )
    vocalizacoes: Mapped[list["Vocalizacao"]] = relationship(
        back_populates="usuario", uselist=False, cascade="all, delete-orphan"
    )
