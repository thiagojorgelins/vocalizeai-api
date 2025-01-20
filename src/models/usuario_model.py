from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, func
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

    participante: Mapped["Participante"] = relationship(
        back_populates="usuario", uselist=False
    )
    classificacoes: Mapped[list["Classificacao"]] = relationship(
        back_populates="usuario"
    )
    audios: Mapped[list["Audio"]] = relationship(back_populates="usuario")
