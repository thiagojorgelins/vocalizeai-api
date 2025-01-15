from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class NivelSuporte(int, Enum):
    NIVEL_1 = 1
    NIVEL_2 = 2
    NIVEL_3 = 3


class GeneroParticipante(str, Enum):
    M = "Masculino"
    F = "Feminino"


class Condicao(str, Enum):
    TEA = "Transtorno do Espectro Autista"
    T21 = "Síndrome de Down"
    PC = "Paralisia Cerebral"
    OUTRA = "Outra"


class ParticipanteBase(BaseModel):
    genero: GeneroParticipante
    idade: int
    nivel_suporte: NivelSuporte
    qtd_palavras: int
    condicao: Condicao


class ParticipanteCreate(ParticipanteBase):
    pass


class ParticipanteUpdate(ParticipanteBase):
    genero: Optional[GeneroParticipante]
    idade: Optional[int]
    nivel_suporte: Optional[NivelSuporte]
    qtd_palavras: Optional[int]
    condicao: Optional[Condicao]


class ParticipanteResponse(ParticipanteBase):
    id: int
    usuario_id: int
    created_at: datetime
    updated_at: datetime
