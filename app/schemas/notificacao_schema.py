from pydantic import BaseModel
from datetime import datetime


class NotificacaoBase(BaseModel):
    tipo: str
    mensagem: str


class NotificacaoCreate(NotificacaoBase):
    pass


class NotificacaoResponse(NotificacaoBase):
    id: int
    lida: bool 
    data_envio: datetime

    class Config:
        from_attributes = True
