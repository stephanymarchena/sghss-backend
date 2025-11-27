from pydantic import BaseModel
from datetime import date, time, datetime

class ProfissionalResumo(BaseModel):
    id: int
    nome: str
    tipo_profissional: str

    class Config:
        from_attributes = True

class AgendaBase(BaseModel):
    profissional_id: int
    data: date
    hora: time

class AgendaCreate(AgendaBase): #vai herdar tudo de AgendaBase 
    pass

class AgendaUpdate(BaseModel):
    """Campos opcionais para PATCH /agendas/{id}"""
    data: date | None = None
    hora: time | None = None
    disponivel: bool | None = None

class AgendaResponse(AgendaBase):
    id: int
    disponivel: bool
    criado_em: datetime
    profissional: ProfissionalResumo

    class Config:
        from_attributes = True
