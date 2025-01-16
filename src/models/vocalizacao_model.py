from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, func
from src.database import Base


class Vocalizacao(Base):
    __tablename__ = "vocalizacao"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String, nullable=False)
    descricao: Mapped[str] = mapped_column(String)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    classificacoes: Mapped[list["Classificacao"]] = relationship(
        back_populates="vocalizacao"
    )
    audios: Mapped[list["Audio"]] = relationship(back_populates="vocalizacao")
