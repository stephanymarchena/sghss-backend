from datetime import datetime
from sqlalchemy import Column, Integer, Date, Time, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Agenda(Base):
    __tablename__ = "agendas"

    id = Column(Integer, primary_key=True, index=True)
    profissional_id = Column(Integer, ForeignKey("profissionais_saude.id"), nullable=False)
    data = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    disponivel = Column(Boolean, default=True, nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow)

    # relacionamento com ProfissionalSaude
    profissional = relationship("ProfissionalSaude", backref="agendas")
