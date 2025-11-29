from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database import Base

class Exame(Base):
    __tablename__ = "exames"

    id = Column(Integer, primary_key=True, index=True)

    # FK → paciente
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False)

    # FK → profissional que solicitou o exame
    profissional_id = Column(Integer, ForeignKey("profissionais_saude.id"), nullable=False)

    # FK opcional → consulta
    consulta_id = Column(Integer, ForeignKey("consultas.id"), nullable=True)

    tipo_exame = Column(String, nullable=False)

    status = Column(String, default="solicitado", nullable=False)  
    # exemplos: solicitado, em_andamento, concluido

    resultado = Column(String, nullable=True)

    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    atualizado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # relações
    paciente = relationship("Paciente", backref="exames")
    profissional = relationship("ProfissionalSaude", backref="exames_solicitados")
    consulta = relationship("Consulta", backref="exames")
