from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database import Base


class Prontuario(Base):
    __tablename__ = "prontuarios"

    id = Column(Integer, primary_key=True, index=True)

    # FK → Paciente.id
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), unique=True, nullable=False)

    # último update no prontuário
    ultima_atualizacao = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # relacionamento 1:N com entradas
    entradas = relationship("EntradaProntuario", back_populates="prontuario", cascade="all, delete-orphan")

    paciente = relationship("Paciente", backref="prontuario")
