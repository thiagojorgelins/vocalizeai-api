from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class QuantidadePalavras(str, Enum):
    NENHUMA = "Não pronuncia nenhuma palavra"
    UM_CINCO = "Pronuncia entre 1 e 5 palavras"
    SEIS_QUINZE = "Pronuncia entre 6 e 15 palavras"
    DEZESSEIS_MAIS = "Pronuncia 16 ou mais palavras"


class NivelSuporte(int, Enum):
    NIVEL_0 = 0
    NIVEL_1 = 1
    NIVEL_2 = 2
    NIVEL_3 = 3
    


class GeneroParticipante(str, Enum):
    M = "Masculino"
    F = "Feminino"
    O = "Outros"


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
