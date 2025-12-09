from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Dict, Set

from app.models.consulta import Consulta
from app.models.paciente import Paciente
from app.models.profissional_saude import ProfissionalSaude
from app.models.agenda import Agenda
from app.schemas.consulta_schema import ConsultaCreate, ConsultaUpdate

from app.services.notificacao_service import criar_notificacao_service
from app.schemas.notificacao_schema import NotificacaoCreate


# -------------------------------------------------------------------
# Máquina de estados: transições de status permitidas
# -------------------------------------------------------------------
TRANSICOES_PERMITIDAS: Dict[str, Set[str]] = {
    "agendada": {"confirmada", "cancelada", "finalizada"},
    "confirmada": {"finalizada", "cancelada"},
    "cancelada": set(),
    "finalizada": set(),
}


def pode_mudar_status(status_atual: str, novo_status: str) -> bool:
    """
    Retorna True se a transição de status for permitida.
    """
    return novo_status in TRANSICOES_PERMITIDAS.get(status_atual, set())


# -------------------------------------------------------------------
# Normalização de datetime (naive -> UTC)
# -------------------------------------------------------------------
def normalizar_datetime(dt: datetime) -> datetime:
    if dt is None:
        return dt
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


# -------------------------------------------------------------------
# AGENDAR CONSULTA
# -------------------------------------------------------------------
def agendar_consulta_service(dados: ConsultaCreate, db: Session) -> Consulta:
    paciente = db.query(Paciente).filter(Paciente.id == dados.paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")

    profissional = db.query(ProfissionalSaude).filter(ProfissionalSaude.id == dados.profissional_id).first()
    if not profissional:
        raise HTTPException(status_code=404, detail="Profissional não encontrado.")

    if paciente.usuario_id == profissional.usuario_id:
        raise HTTPException(
            status_code=400,
            detail="Um profissional de saúde não pode agendar uma consulta para si mesmo."
        )

    data_hora = normalizar_datetime(dados.data_hora)
    if data_hora <= datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="A data/hora da consulta deve ser no futuro.")

    # procurar slot disponível
    slot = db.query(Agenda).filter(
        Agenda.profissional_id == dados.profissional_id,
        Agenda.data == data_hora.date(),
        Agenda.hora == data_hora.time(),
        Agenda.disponivel == True
    ).with_for_update(read=False).first()

    if not slot:
        raise HTTPException(status_code=400, detail="Horário indisponível na agenda do profissional.")

    # reservar slot
    slot.disponivel = False
    db.commit()

    consulta = Consulta(
        data_hora=data_hora,
        observacoes=dados.observacoes,
        paciente_id=dados.paciente_id,
        profissional_id=dados.profissional_id,
        status="agendada"
    )
    db.add(consulta)
    db.commit()
    db.refresh(consulta)

    # notificação (silenciosa em falha)
    try:
        criar_notificacao_service(
            paciente.usuario_id,
            NotificacaoCreate(
                tipo="consulta",
                mensagem=f"Consulta agendada para {consulta.data_hora} com {profissional.nome}."
            ),
            db
        )
    except Exception:
        pass

    return consulta


# -------------------------------------------------------------------
# CONSULTA POR ID (representação amigável)
# -------------------------------------------------------------------
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


# -------------------------------------------------------------------
# LISTAR CONSULTAS
# -------------------------------------------------------------------
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


# -------------------------------------------------------------------
# REAGENDAR / ATUALIZAR CONSULTA
# -------------------------------------------------------------------
def atualizar_consulta_service(consulta_id: int, dados: ConsultaUpdate, db: Session) -> Consulta:
    consulta = db.query(Consulta).filter(Consulta.id == consulta_id).first()
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada.")

    if consulta.status in ["cancelada", "finalizada"]:
        raise HTTPException(
            status_code=400,
            detail="Não é permitido reagendar uma consulta cancelada ou finalizada."
        )

    dados_dict = dados.model_dump(exclude_unset=True)

    if "data_hora" in dados_dict:
        novo_dt = normalizar_datetime(dados_dict["data_hora"])

        if novo_dt <= datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="A nova data/hora deve ser no futuro.")

        novo_slot = db.query(Agenda).filter(
            Agenda.profissional_id == consulta.profissional_id,
            Agenda.data == novo_dt.date(),
            Agenda.hora == novo_dt.time(),
            Agenda.disponivel == True
        ).first()

        if not novo_slot:
            raise HTTPException(status_code=400, detail="Novo horário indisponível.")

        novo_slot.disponivel = False
        db.commit()

        antigo_slot = db.query(Agenda).filter(
            Agenda.profissional_id == consulta.profissional_id,
            Agenda.data == consulta.data_hora.date(),
            Agenda.hora == consulta.data_hora.time()
        ).first()

        if antigo_slot:
            antigo_slot.disponivel = True
            db.commit()

        consulta.data_hora = novo_dt

    for campo, valor in dados_dict.items():
        if campo != "data_hora":
            setattr(consulta, campo, valor)

    db.commit()
    db.refresh(consulta)
    return consulta


# -------------------------------------------------------------------
# MUDANÇA DE STATUS (centralizada)
# -------------------------------------------------------------------
def _mudar_status_obj(consulta_obj: Consulta, novo_status: str, db: Session) -> Consulta:
    estado_atual = consulta_obj.status

    if not pode_mudar_status(estado_atual, novo_status):
        raise HTTPException(
            status_code=400,
            detail=f"Transição de '{estado_atual}' para '{novo_status}' não é permitida."
        )

    consulta_obj.status = novo_status
    db.commit()
    db.refresh(consulta_obj)
    return consulta_obj


# -------------------------------------------------------------------
# CONFIRMAR CONSULTA
# -------------------------------------------------------------------
def confirmar_consulta_service(consulta_id: int, db: Session) -> Consulta:
    consulta = db.query(Consulta).filter(Consulta.id == consulta_id).first()
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada.")

    consulta = _mudar_status_obj(consulta, "confirmada", db)

    try:
        criar_notificacao_service(
            consulta.paciente.usuario_id,
            NotificacaoCreate(
                tipo="consulta",
                mensagem=f"Sua consulta em {consulta.data_hora} foi CONFIRMADA."
            ),
            db
        )
    except Exception:
        pass

    return consulta


# -------------------------------------------------------------------
# CANCELAR CONSULTA
# -------------------------------------------------------------------
def cancelar_consulta_service(consulta_id: int, db: Session) -> Consulta:
    consulta = db.query(Consulta).filter(Consulta.id == consulta_id).first()
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada.")

    consulta = _mudar_status_obj(consulta, "cancelada", db)

    slot = db.query(Agenda).filter(
        Agenda.profissional_id == consulta.profissional_id,
        Agenda.data == consulta.data_hora.date(),
        Agenda.hora == consulta.data_hora.time()
    ).first()

    if slot:
        slot.disponivel = True
        db.commit()

    try:
        criar_notificacao_service(
            consulta.paciente.usuario_id,
            NotificacaoCreate(
                tipo="consulta",
                mensagem=f"Sua consulta em {consulta.data_hora} foi CANCELADA."
            ),
            db
        )
    except Exception:
        pass

    return consulta


# -------------------------------------------------------------------
# FINALIZAR CONSULTA
# -------------------------------------------------------------------
def finalizar_consulta_service(consulta_id: int, db: Session) -> Consulta:
    consulta = db.query(Consulta).filter(Consulta.id == consulta_id).first()
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada.")

    consulta = _mudar_status_obj(consulta, "finalizada", db)

    try:
        criar_notificacao_service(
            consulta.paciente.usuario_id,
            NotificacaoCreate(
                tipo="consulta",
                mensagem=f"Consulta em {consulta.data_hora} foi FINALIZADA."
            ),
            db
        )
    except Exception:
        pass

    return consulta


# -------------------------------------------------------------------
# DELETAR CONSULTA
# -------------------------------------------------------------------
def deletar_consulta_service(consulta_id: int, db: Session):
    consulta = db.query(Consulta).filter(Consulta.id == consulta_id).first()
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada.")

    # liberar slot somente se não tiver sido finalizada
    if consulta.status != "finalizada":
        slot = db.query(Agenda).filter(
            Agenda.profissional_id == consulta.profissional_id,
            Agenda.data == consulta.data_hora.date(),
            Agenda.hora == consulta.data_hora.time()
        ).first()

        if slot:
            slot.disponivel = True
            db.commit()

    db.delete(consulta)
    db.commit()

    return {"message": "Consulta deletada com sucesso."}
