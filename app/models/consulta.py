from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Consulta(Base):
    __tablename__ = "consultas"

    id = Column(Integer, primary_key=True, index=True)
    data_hora = Column(DateTime, nullable=False)
    status = Column(String, default="agendada", nullable=False)
    observacoes = Column(String, nullable=True)

    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False)
    profissional_id = Column(Integer, ForeignKey("profissionais_saude.id"), nullable=False)

    paciente = relationship("Paciente", backref="consultas")
    profissional = relationship("ProfissionalSaude", backref="consultas")
