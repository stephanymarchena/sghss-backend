from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database import Base


class Notificacao(Base):
    __tablename__ = "notificacoes"

    id = Column(Integer, primary_key=True, index=True)

    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    tipo = Column(String, nullable=False)          # ex: consulta, exame, sistema
    mensagem = Column(String, nullable=False)
    lida = Column(Boolean, default=False)

    data_envio = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    usuario = relationship("Usuario", backref="notificacoes")
