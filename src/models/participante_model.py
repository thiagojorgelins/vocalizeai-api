from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, DateTime, func
from src.database import Base


class Participante(Base):
    __tablename__ = "participante"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    genero: Mapped[str] = mapped_column(String, nullable=False)
    idade: Mapped[int] = mapped_column(nullable=False)
    nivel_suporte: Mapped[int] = mapped_column(nullable=False)
    qtd_palavras: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    usuario: Mapped["Usuario"] = relationship(back_populates="participante")
    audios: Mapped[list["Audio"]] = relationship(
        back_populates="participante", cascade="all, delete-orphan"
    )
