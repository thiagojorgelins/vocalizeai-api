from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class QuantidadePalavras(str, Enum):
    NENHUMA = "Nenhuma palavra"
    UM_CINCO = "Entre 1 - 5"
    SEIS_DEZ = "Entre 6 - 10"
    ONZE_VINTE = "Entre 11 - 20"


class NivelSuporte(int, Enum):
    NIVEL_1 = 1
    NIVEL_2 = 2
    NIVEL_3 = 3


class GeneroParticipante(str, Enum):
    M = "Masculino"
    F = "Feminino"


class ParticipanteBase(BaseModel):
    genero: GeneroParticipante
    idade: int
    nivel_suporte: NivelSuporte
    qtd_palavras: QuantidadePalavras


class ParticipanteCreate(ParticipanteBase):
    pass


class ParticipanteUpdate(ParticipanteBase):
    genero: Optional[GeneroParticipante]
    idade: Optional[int]
    nivel_suporte: Optional[NivelSuporte]
    qtd_palavras: Optional[QuantidadePalavras]


class ParticipanteResponse(ParticipanteBase):
    id: int
    id_usuario: int
    created_at: datetime
    updated_at: datetime
