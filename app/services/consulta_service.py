# app/services/consulta_service.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.models.consulta import Consulta
from app.models.paciente import Paciente
from app.models.profissional_saude import ProfissionalSaude
from app.models.agenda import Agenda
from app.schemas.consulta_schema import ConsultaCreate, ConsultaUpdate

def agendar_consulta_service(dados: ConsultaCreate, db: Session) -> Consulta:
    """
    Cria uma consulta somente se existir um slot na Agenda para o profissional + data + hora,
    e esse slot estiver disponivel == True. Reserva o slot (disponivel = False) antes de criar.
    """
    # validações básicas 
    paciente = db.query(Paciente).filter(Paciente.id == dados.paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")

    profissional = db.query(ProfissionalSaude).filter(ProfissionalSaude.id == dados.profissional_id).first()
    if not profissional:
        raise HTTPException(status_code=404, detail="Profissional não encontrado.")
    
    # Um profissional não pode ser paciente de si mesmo
    if paciente.usuario_id == profissional.usuario_id:
        raise HTTPException(
            status_code=400,
            detail="Um profissional de saúde não pode agendar uma consulta para si mesmo."
        )

    if dados.data_hora <= datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="A data/hora da consulta deve ser no futuro.")

    # procurar slot disponível na agenda
    slot_data = dados.data_hora.date()
    slot_hora = dados.data_hora.time()

    slot = db.query(Agenda).filter(
        Agenda.profissional_id == dados.profissional_id,
        Agenda.data == slot_data,
        Agenda.hora == slot_hora,
        Agenda.disponivel == True
    ).with_for_update(read=False).first()  # tenta evitar corrida simples (bd)

    if not slot:
        raise HTTPException(status_code=400, detail="Horário indisponível. Verifique a agenda do profissional.")

    # reservar o slot (marcar indisponível) antes de criar a consulta
    slot.disponivel = False
    db.add(slot)
    db.commit()
    db.refresh(slot)

    # criar a consulta
    consulta = Consulta(
        data_hora=dados.data_hora,
        observacoes=getattr(dados, "observacoes", None),
        paciente_id=dados.paciente_id,
        profissional_id=dados.profissional_id,
        status="agendada"
    )
    db.add(consulta)
    db.commit()
    db.refresh(consulta)
    return consulta


def buscar_consulta_por_id_service(consulta_id: int, db: Session):
    """
    retorna representação mais intuitiva nos testes.
    """
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
    """
    regra pra consulta finalizada ou cancelada:
    - Se a consulta estiver cancelada ou finalizada >> NÃO permite reagendar.
    - Se estiver agendada/confirmada >> permite reagendar.
    - Ao reagendar vai:
        *- reserva novo slot
        *- libera antigo
    """
    consulta = db.query(Consulta).filter(Consulta.id == consulta_id).first()
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada.")

    # Bloqueio consulta finalizada ou cancelada
    if consulta.status in ["cancelada", "finalizada"]:
        raise HTTPException(
            status_code=400,
            detail="Não é permitido reagendar uma consulta cancelada ou finalizada. Crie uma nova consulta."
        )

    dados_dict = dados.model_dump(exclude_unset=True)

    # se for reagendar (data_hora no presente apanas)
    if "data_hora" in dados_dict:
        novo_dt = dados_dict["data_hora"]

        # não permite agendar datas que já passaram
        if novo_dt <= datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="A nova data/hora deve ser no futuro.")

        # procura novo slot
        novo_slot = db.query(Agenda).filter(
            Agenda.profissional_id == consulta.profissional_id,
            Agenda.data == novo_dt.date(),
            Agenda.hora == novo_dt.time(),
            Agenda.disponivel == True
        ).first()

        if not novo_slot:
            raise HTTPException(
                status_code=400,
                detail="Novo horário indisponível na agenda do profissional."
            )

        # reserva novo horário
        novo_slot.disponivel = False
        db.add(novo_slot)
        db.commit()
        db.refresh(novo_slot)

        # libera horário antigo
        antigo_slot = db.query(Agenda).filter(
            Agenda.profissional_id == consulta.profissional_id,
            Agenda.data == consulta.data_hora.date(),
            Agenda.hora == consulta.data_hora.time()
        ).first()
        if antigo_slot:
            antigo_slot.disponivel = True
            db.add(antigo_slot)
            db.commit()
            db.refresh(antigo_slot)

        # registra nova data/hora
        consulta.data_hora = novo_dt

    # aplica demais campos (observacoes da consulta)
    for campo, valor in dados_dict.items():
        if campo == "data_hora":
            continue
        setattr(consulta, campo, valor)

    db.commit()
    db.refresh(consulta)
    return consulta



def _mudar_status_obj(consulta_obj: Consulta, novo_status: str, db: Session) -> Consulta:
    """
    atualiza o status em um objeto Consulta ORM e salva
    """
    consulta_obj.status = novo_status
    db.commit()
    db.refresh(consulta_obj)
    return consulta_obj


def confirmar_consulta_service(consulta_id: int, db: Session) -> Consulta:
    """
    confirma a consulta (status --> confirmada)
    trabalha com o objeto Consulta diretamente
    """
    consulta = db.query(Consulta).filter(Consulta.id == consulta_id).first()
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada.")
    return _mudar_status_obj(consulta, "confirmada", db)


def cancelar_consulta_service(consulta_id: int, db: Session) -> Consulta:
    """
    Cancela a consulta (status --> cancelada) e libera o slot correspondente na Agenda, se existir
    """
    consulta = db.query(Consulta).filter(Consulta.id == consulta_id).first()
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada.")

    # mudar status
    consulta = _mudar_status_obj(consulta, "cancelada", db)

    # tentar liberar slot correspondente (mesmo profissional/data/hora)
    slot = db.query(Agenda).filter(
        Agenda.profissional_id == consulta.profissional_id,
        Agenda.data == consulta.data_hora.date(),
        Agenda.hora == consulta.data_hora.time()
    ).first()

    if slot:
        slot.disponivel = True
        db.add(slot)
        db.commit()
        db.refresh(slot)

    return consulta


def finalizar_consulta_service(consulta_id: int, db: Session) -> Consulta:
    consulta = db.query(Consulta).filter(Consulta.id == consulta_id).first()
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada.")
    return _mudar_status_obj(consulta, "finalizada", db)


def deletar_consulta_service(consulta_id: int, db: Session):
    """
    Aqui ao deletar, tenta liberar o slot por segurança, depois remove a consulta
    """
    consulta = db.query(Consulta).filter(Consulta.id == consulta_id).first()
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada.")

    # vai tentar liberar slot associado
    slot = db.query(Agenda).filter(
        Agenda.profissional_id == consulta.profissional_id,
        Agenda.data == consulta.data_hora.date(),
        Agenda.hora == consulta.data_hora.time()
    ).first()

    if slot:
        slot.disponivel = True
        db.add(slot)
        db.commit()
        db.refresh(slot)

    db.delete(consulta)
    db.commit()
    return {"message": "Consulta deletada com sucesso."}
