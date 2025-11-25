from pydantic import BaseModel
from typing import Literal
from datetime import datetime


class PacienteResumo(BaseModel):
    id: int
    nome: str


class ProfissionalResumo(BaseModel):
    id: int
    nome: str
    tipo_profissional: str



class ConsultaBase(BaseModel):
    data_hora: datetime
    observacoes: str | None = None
    paciente_id: int
    profissional_id: int

class ConsultaCreate(ConsultaBase):
    pass

class ConsultaUpdate(BaseModel):
    data_hora: datetime | None = None
    observacoes: str | None = None
    paciente_id: int | None = None
    profissional_id: int | None = None
    status: Literal["agendada","confirmada","cancelada","finalizada"] | None = None

class ConsultaResponse(BaseModel):
    id: int
    data_hora: datetime
    status: str
    observacoes: str | None

    paciente: PacienteResumo
    profissional: ProfissionalResumo

    class Config:
        from_attributes = True
