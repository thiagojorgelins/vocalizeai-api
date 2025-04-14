from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, DateTime, func
from src.database import Base


class Audio(Base):
    __tablename__ = "audio"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome_arquivo: Mapped[str] = mapped_column(String, nullable=False)
    id_vocalizacao: Mapped[int] = mapped_column(
        ForeignKey("vocalizacao.id"), nullable=False
    )
    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False
    )
    id_participante: Mapped[int] = mapped_column(
        ForeignKey("participante.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    vocalizacao: Mapped["Vocalizacao"] = relationship(back_populates="audios")
    usuario: Mapped["Usuario"] = relationship(back_populates="audios")
    participante: Mapped["Participante"] = relationship(back_populates="audios")
