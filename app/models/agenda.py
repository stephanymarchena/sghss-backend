from sqlalchemy import Column, Integer, Date, Time, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class Agenda(Base):
    __tablename__ = "agendas"

    id = Column(Integer, primary_key=True, index=True)
    profissional_id = Column(Integer, ForeignKey("profissionais_saude.id"), nullable=False)
    data = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    disponivel = Column(Boolean, default=True)

    # CORREÇÃO AQUI:
    profissional = relationship("ProfissionalSaude", backref="agendas")

    __table_args__ = (
        UniqueConstraint(
            "profissional_id",
            "data",
            "hora",
            name="unique_horario_profissional"
        ),
    )
