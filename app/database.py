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
   # Modelos de usuário e perfis vinculados
    import app.models.usuario
    import app.models.paciente
    import app.models.profissional_saude

    # Modelos de funções do sistema
    import app.models.consulta
    import app.models.agenda  

    
   # Cria todas as tabelas que ainda não existem
    Base.metadata.create_all(bind=engine)
    print(">>> Banco de dados inicializado. As tabelas foram verificadas/criadas.")



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()