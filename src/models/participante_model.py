from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey
from src.database import Base


class Participante(Base):
    __tablename__ = "participante"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuario.id"), nullable=False, unique=True
    )
    genero: Mapped[str] = mapped_column(String, nullable=False)
    idade: Mapped[int] = mapped_column(nullable=False)
    nivel_suporte: Mapped[int] = mapped_column(nullable=False)
    qtd_palavras: Mapped[int] = mapped_column(nullable=False)
    condicao: Mapped[str] = mapped_column(String, nullable=False)

    usuario: Mapped["Usuario"] = relationship(back_populates="participante")
