from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, DateTime, func
from src.database import Base


class Classificacao(Base):
    __tablename__ = "classificacao"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuario.id"), nullable=False)
    id_vocalizacao: Mapped[int] = mapped_column(
        ForeignKey("vocalizacao.id"), nullable=False
    )
    predicao_modelo: Mapped[float] = mapped_column(nullable=False)
    avaliacao_usuario: Mapped[str] = mapped_column(String)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    usuario: Mapped["Usuario"] = relationship(back_populates="classificacoes")
    vocalizacao: Mapped["Vocalizacao"] = relationship(back_populates="classificacoes")
