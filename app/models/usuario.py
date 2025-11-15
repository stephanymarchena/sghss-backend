from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime
from datetime import datetime, timezone
from app.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    cpf = Column(String, unique=True, index=True, nullable=False)
    telefone = Column(String, nullable=True)
    endereco = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False)

    ativo = Column(Boolean, default=True)
    sexo = Column(String, nullable=True)
    data_nascimento = Column(Date, nullable=True)

    criado_em = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    atualizado_em = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

print(">>> Model Usuario foi carregado!")
