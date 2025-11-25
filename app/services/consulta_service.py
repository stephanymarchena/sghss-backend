from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.consulta import Consulta
from app.models.paciente import Paciente
from app.models.profissional_saude import ProfissionalSaude
from app.schemas.consulta_schema import ConsultaCreate, ConsultaUpdate

def agendar_consulta_service(dados: ConsultaCreate, db: Session) -> Consulta:
    # validações basicas
    paciente = db.query(Paciente).filter(Paciente.id == dados.paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")

    profissional = db.query(ProfissionalSaude).filter(ProfissionalSaude.id == dados.profissional_id).first()
    if not profissional:
        raise HTTPException(status_code=404, detail="Profissional não encontrado.")

    if dados.data_hora <= datetime.utcnow():
        raise HTTPException(status_code=400, detail="A data/hora da consulta deve ser no futuro.")

    consulta = Consulta(
        data_hora=dados.data_hora,
        observacoes=dados.observacoes,
        paciente_id=dados.paciente_id,
        profissional_id=dados.profissional_id,
        status="agendada"
    )
    db.add(consulta)
    db.commit()
    db.refresh(consulta)
    return consulta

def buscar_consulta_por_id_service(consulta_id: int, db: Session):
    c = db.query(Consulta).filter(Consulta.id == consulta_id).first()

    if not c:
        raise HTTPException(status_code=404, detail="Consulta não encontrada.")

    return {
        "id": c.id,
        "data_hora": c.data_hora,
        "status": c.status,
        "observacoes": c.observacoes,

        "paciente": {
            "id": c.paciente.id,
            "nome": c.paciente.usuario.nome
        },

        "profissional": {
            "id": c.profissional.id,
            "nome": c.profissional.usuario.nome,
            "tipo_profissional": c.profissional.tipo_profissional
        }
    }


def listar_consultas_service(db: Session):
    consultas = db.query(Consulta).all()
    resultados = []

    for c in consultas:
        resultados.append({
            "id": c.id,
            "data_hora": c.data_hora,
            "status": c.status,
            "observacoes": c.observacoes,

            "paciente": {
                "id": c.paciente.id,
                "nome": c.paciente.usuario.nome
            },

            "profissional": {
                "id": c.profissional.id,
                "nome": c.profissional.usuario.nome,
                "tipo_profissional": c.profissional.tipo_profissional
            }
        })

    return resultados


def atualizar_consulta_service(consulta_id: int, dados: ConsultaUpdate, db: Session) -> Consulta:
    consulta = db.query(Consulta).filter(Consulta.id == consulta_id).first()
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada.")
    dados_dict = dados.model_dump(exclude_unset=True)
    # permitir atualizacao parcial (por exemplo reagendar)
    if "data_hora" in dados_dict:
        if dados_dict["data_hora"] <= datetime.utcnow():
            raise HTTPException(status_code=400, detail="A nova data/hora deve ser no futuro.")
    for campo, valor in dados_dict.items():
        setattr(consulta, campo, valor)
    db.commit()
    db.refresh(consulta)
    return consulta

def _mudar_status(consulta: Consulta, novo_status: str, db: Session) -> Consulta:
    consulta.status = novo_status
    db.commit()
    db.refresh(consulta)
    return consulta

def confirmar_consulta_service(consulta_id: int, db: Session) -> Consulta:
    consulta = buscar_consulta_por_id_service(consulta_id, db)
    return _mudar_status(consulta, "confirmada", db)

def cancelar_consulta_service(consulta_id: int, db: Session) -> Consulta:
    consulta = buscar_consulta_por_id_service(consulta_id, db)
    return _mudar_status(consulta, "cancelada", db)

def finalizar_consulta_service(consulta_id: int, db: Session) -> Consulta:
    consulta = buscar_consulta_por_id_service(consulta_id, db)
    return _mudar_status(consulta, "finalizada", db)

def deletar_consulta_service(consulta_id: int, db: Session):
    consulta = db.query(Consulta).filter(Consulta.id == consulta_id).first()
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada.")
    db.delete(consulta)
    db.commit()
    return {"message": "Consulta deletada com sucesso."}
