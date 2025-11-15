# Arquivo: app/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./sghss.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def inicializar_bd():
    # Este import é crucial para garantir que a Base conheça a classe Usuario
    import app.models.usuario  
    
    # Cria a tabela 'usuarios' se ela ainda não existir
    Base.metadata.create_all(bind=engine)
    print(">>> Banco de dados inicializado. As tabelas foram verificadas/criadas.")


# >>> REMOVIDA: A chamada inicializar_bd() não deve mais estar aqui.


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()