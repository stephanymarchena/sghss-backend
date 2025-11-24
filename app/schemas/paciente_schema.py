from pydantic import BaseModel


# Schema base - Campos comuns entre create/response
class PacienteBase(BaseModel):
    usuario_id: int


# Para criação de paciente, mesma coisa da base por enquanto.
class PacienteCreate(PacienteBase):
    pass


# Para atualização parcial (PATCH)}
# no futuro pode haver atributos que precisam ser atualizados. 
class PacienteUpdate(BaseModel):
    pass


# Para resposta da API
class PacienteResponse(PacienteBase):
    id: int

    class Config:
        from_attributes = True
