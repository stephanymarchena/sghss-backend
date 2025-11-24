from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Paciente(Base):
    __tablename__ = "pacientes"

    # ID próprio do paciente
    id = Column(Integer, primary_key=True, index=True)

    # FK -> Usuario.id  (um paciente sempre tem um usuario!)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), unique=True, nullable=False)

    # Relacionamento com a tabela Usuario
    usuario = relationship("Usuario", backref="paciente")

    # Relacionamento com Consulta (será ativado no futuro)
    # consultas = relationship("Consulta", back_populates="paciente")
