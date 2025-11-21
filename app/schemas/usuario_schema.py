from pydantic import BaseModel, EmailStr
from datetime import date, datetime


#schema base - criação dos dados comuns do usuario atributos normais 
class UsuarioBase(BaseModel):
    nome: str
    cpf: str
    telefone: str | None = None
    endereco: str | None = None
    email: EmailStr
    sexo: str | None = None
    data_nascimento: date | None = None

#schema de criação - senha vai vir como texto puro, vai ser convertida pra hash depois 

class UsuarioCreate(UsuarioBase):
    senha: str

#schema de resposta - somente depois de criar vai trazer esses dados aqui.
class UsuarioResponse(UsuarioBase):
    id: int
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True  


# Classe para filtrar no schema o que vai ser listado do GET de todos os usuarios
class UsuarioListResponse(BaseModel):
    id: int
    nome: str
    email: EmailStr
    ativo: bool
    criado_em: datetime

    class Config:
        from_attributes = True
