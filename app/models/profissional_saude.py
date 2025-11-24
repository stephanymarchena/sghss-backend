from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class ProfissionalSaude(Base):
    __tablename__ = "profissionais_saude"

    id = Column(Integer, primary_key=True, index=True)

    # FK --> Usuario.id
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), unique=True, nullable=False)

    # tipo: "medico", "enfermeiro", "tecnico"
    tipo_profissional = Column(String, nullable=False)

    # CRM, COREN, registro técnico — tudo aqui
    registro_profissional = Column(String, nullable=False)

    # Relacionamento com Usuario (1:1)
    usuario = relationship("Usuario", backref="profissional_saude")

    # Relacionamento com Consulta (pro futuro)
    # consultas = relationship("Consulta", back_populates="profissional")
