from datetime import datetime
from pydantic import BaseModel

# ---------- Entradas do Prontuário ----------

class EntradaProntuarioBase(BaseModel):
    texto: str
    tipo: str = "anotacao"
    consulta_id: int | None = None


class EntradaProntuarioCreate(EntradaProntuarioBase):
    pass


class EntradaProntuarioResponse(EntradaProntuarioBase):
    id: int
    data_hora: datetime

    model_config = {"from_attributes": True}


# ---------- Prontuário ----------

class ProntuarioBase(BaseModel):
    paciente_id: int


class ProntuarioResponse(BaseModel):
    id: int
    paciente_id: int
    ultima_atualizacao: datetime
    entradas: list[EntradaProntuarioResponse] = []

    model_config = {"from_attributes": True}
