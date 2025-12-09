from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.paciente import Paciente
from app.models.usuario import Usuario
from app.models.prontuario import Prontuario  

from app.schemas.paciente_schema import (
    PacienteCreate,
    PacienteUpdate
)


def criar_paciente_service(dados: PacienteCreate, db: Session) -> Paciente:
    # Verificar se o usuário existe
    usuario = db.query(Usuario).filter(Usuario.id == dados.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    # Verificar se já existe paciente para este usuário
    paciente_existente = db.query(Paciente).filter(Paciente.usuario_id == dados.usuario_id).first()
    if paciente_existente:
        raise HTTPException(status_code=400, detail="Este usuário já está associado a um paciente.")

    # Criar paciente
    paciente = Paciente(usuario_id=dados.usuario_id)
    db.add(paciente)
    db.commit()
    db.refresh(paciente)

    # -------------------------------------------------------
    # Criar prontuário automaticamente
    # -------------------------------------------------------
    prontuario = Prontuario(paciente_id=paciente.id)
    db.add(prontuario)
    db.commit()
    # refresh é opcional aqui
    db.refresh(prontuario)

    return paciente


def buscar_paciente_por_id_service(paciente_id: int, db: Session) -> Paciente:
    paciente = db.query(Paciente).filter(Paciente.id == paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    return paciente


def listar_pacientes_service(db: Session) -> list[Paciente]:
    return db.query(Paciente).all()


def atualizar_paciente_service(paciente_id: int, dados: PacienteUpdate, db: Session) -> Paciente:
    paciente = db.query(Paciente).filter(Paciente.id == paciente_id).first()

    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")

    dados_dict = dados.model_dump(exclude_unset=True)

    #No momento nenhum campo próprio pode ser atualizado, mas deixa aberto pra ser escalavel
    for campo, valor in dados_dict.items():
        setattr(paciente, campo, valor)

    db.commit()
    db.refresh(paciente)
    return paciente


def deletar_paciente_service(paciente_id: int, db: Session):
    paciente = db.query(Paciente).filter(Paciente.id == paciente_id).first()

    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")

    db.delete(paciente)
    db.commit()
    return {"message": "Paciente deletado com sucesso."}
