from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timezone

from app.models.prontuario import Prontuario
from app.models.entrada_prontuario import EntradaProntuario
from app.schemas.prontuario_schema import EntradaProntuarioCreate


# ---------- Buscar Prontuário ----------

def get_prontuario_by_paciente_id(db: Session, paciente_id: int) -> Prontuario:
    prontuario = db.query(Prontuario).filter(Prontuario.paciente_id == paciente_id).first()
    if not prontuario:
        raise HTTPException(
            status_code=404,
            detail="Prontuário não encontrado para este paciente."
        )
    return prontuario


# ---------- Criar Prontuário ----------

def criar_prontuario(db: Session, paciente_id: int) -> Prontuario:
    # impede prontuário duplicado
    existente = db.query(Prontuario).filter(Prontuario.paciente_id == paciente_id).first()
    if existente:
        raise HTTPException(
            status_code=400,
            detail="Este paciente já possui um prontuário."
        )

    prontuario = Prontuario(
        paciente_id=paciente_id,
        ultima_atualizacao=datetime.now(timezone.utc)
    )

    db.add(prontuario)
    db.commit()
    db.refresh(prontuario)
    return prontuario


# ---------- Adicionar Entrada ----------

def adicionar_entrada(db: Session, paciente_id: int, dados: EntradaProntuarioCreate):
    prontuario = get_prontuario_by_paciente_id(db, paciente_id)

    entrada = EntradaProntuario(
        prontuario_id=prontuario.id,
        texto=dados.texto,
        tipo=dados.tipo,
        consulta_id=dados.consulta_id,
        data_hora=datetime.now(timezone.utc)
    )

    db.add(entrada)

    # atualizar timestamp do prontuário
    prontuario.ultima_atualizacao = datetime.now(timezone.utc)
    db.add(prontuario)

    db.commit()
    db.refresh(entrada)
    return entrada


# ---------- Listar Entradas ----------
def listar_entradas(db: Session, paciente_id: int):
    prontuario = get_prontuario_by_paciente_id(db, paciente_id)

    entradas = (
        db.query(EntradaProntuario)
        .filter(EntradaProntuario.prontuario_id == prontuario.id)
        .order_by(EntradaProntuario.data_hora.desc())
        .all()
    )

    return entradas
