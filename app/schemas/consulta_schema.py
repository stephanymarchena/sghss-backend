from datetime import datetime
from pydantic import BaseModel

#RESUMOS 

class PacienteResumo(BaseModel):
    id: int
    nome: str

    model_config = {"from_attributes": True} 


class ProfissionalResumo(BaseModel):
    id: int
    nome: str
    tipo_profissional: str

    model_config = {"from_attributes": True}


#CONSULTA BASE 

class ConsultaBase(BaseModel):
    data_hora: datetime
    observacoes: str | None = None


#CREATE E UPDATE 

class ConsultaCreate(ConsultaBase):
    paciente_id: int
    profissional_id: int


class ConsultaUpdate(BaseModel):
    data_hora: datetime | None = None
    observacoes: str | None = None


#RESPOSTA COMPLETA 

class ConsultaResponse(BaseModel):
    id: int
    data_hora: datetime
    status: str
    observacoes: str | None

    paciente: PacienteResumo
    profissional: ProfissionalResumo

    model_config = {"from_attributes": True} #objeto ORM
