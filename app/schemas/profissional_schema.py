from pydantic import BaseModel, Field
from typing import Literal

class UsuarioResumo(BaseModel):
    id: int
    nome: str


# Campos comuns para criação e resposta || aceitar somente medico, enfermeiro e tecnico 
class ProfissionalBase(BaseModel):
    usuario_id: int
    tipo_profissional: Literal["medico", "enfermeiro", "tecnico"] = Field(
        description="Tipo de profissional da saúde"
    )
    registro_profissional: str


# criação (POST)
class ProfissionalCreate(ProfissionalBase):
    pass


#  atualização parcial (PATCH)
class ProfissionalUpdate(BaseModel):
    tipo_profissional: Literal["medico", "enfermeiro", "tecnico"] | None = None
    registro_profissional: str | None = None


#  resposta da API
class ProfissionalResponse(BaseModel):
    id: int
    tipo_profissional: str
    registro_profissional: str
    usuario: UsuarioResumo

    class Config:
        from_attributes = True
