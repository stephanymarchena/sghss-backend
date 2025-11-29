from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database import Base


class EntradaProntuario(Base):
    __tablename__ = "entradas_prontuario"

    id = Column(Integer, primary_key=True, index=True)

    prontuario_id = Column(Integer, ForeignKey("prontuarios.id"), nullable=False)

    texto = Column(String, nullable=False)
    tipo = Column(String, default="anotacao")  # opcional: evolucao, prescricao, exame, etc
    data_hora = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # FK opcional → Consulta.id
    consulta_id = Column(Integer, ForeignKey("consultas.id"), nullable=True)

    # relacionamentos
    prontuario = relationship("Prontuario", back_populates="entradas")
    consulta = relationship("Consulta", backref="entrada_prontuario")
