from pydantic import BaseModel
from datetime import datetime


class ExameBase(BaseModel):
    tipo_exame: str
    consulta_id: int | None = None


class ExameCreate(ExameBase):
    paciente_id: int
    profissional_id: int


class ExameUpdate(BaseModel):
    status: str | None = None
    resultado: str | None = None


class ExameResponse(BaseModel):
    id: int
    paciente_id: int
    profissional_id: int
    consulta_id: int | None
    tipo_exame: str
    status: str
    resultado: str | None
    criado_em: datetime
    atualizado_em: datetime

    model_config = {"from_attributes": True}
