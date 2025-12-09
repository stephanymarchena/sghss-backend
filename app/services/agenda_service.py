from sqlalchemy.orm import Session, joinedload
from datetime import date
from typing import List
from fastapi import HTTPException

from app.models.agenda import Agenda

def create_agenda(db: Session, dados) -> Agenda:
    #cria um horário na agenda
    agenda = Agenda(
        profissional_id=dados.profissional_id,
        data=dados.data,
        hora=dados.hora,
        disponivel=True
    )

    db.add(agenda)
    db.commit()
    db.refresh(agenda)
    return agenda


def get_agenda(db: Session, agenda_id: int) -> Agenda | None:
    #busca uma agenda pelo id
    return db.query(Agenda).filter(Agenda.id == agenda_id).first()


#lista todos os horários de um profissional
def listar_agenda_profissional(db: Session, profissional_id: int) -> List[Agenda]:
    return (
        db.query(Agenda)
        .options(joinedload(Agenda.profissional))
        .filter(Agenda.profissional_id == profissional_id)
        .order_by(Agenda.data, Agenda.hora)
        .all()
    )


def listar_disponiveis(db: Session, profissional_id: int, data: date) -> List[Agenda]:
    return (
        db.query(Agenda)
        .options(joinedload(Agenda.profissional))
        .filter(
            Agenda.profissional_id == profissional_id,
            Agenda.data == data,
            Agenda.disponivel == True
        )
        .order_by(Agenda.hora)
        .all()
    )


def reservar_horario(db: Session, agenda_id: int) -> Agenda:
    # marca um horário como indisponível (tipo reserva)
    agenda = get_agenda(db, agenda_id)

    if not agenda:
        raise HTTPException(status_code=404, detail="Horário não encontrado.")

    if not agenda.disponivel:
        raise HTTPException(status_code=400, detail="Horário já está reservado.")

    agenda.disponivel = False
    db.commit()
    db.refresh(agenda)
    return agenda


def liberar_horario(db: Session, agenda_id: int) -> Agenda:
    #marca um horário como disponível novamente
    agenda = get_agenda(db, agenda_id)

    if not agenda:
        raise HTTPException(status_code=404, detail="Horário não encontrado.")

    agenda.disponivel = True
    db.commit()
    db.refresh(agenda)
    return agenda


def atualizar_agenda(db: Session, agenda_id: int, dados) -> Agenda:
    #atualiza um horário existente
    agenda = get_agenda(db, agenda_id)

    if not agenda:
        raise HTTPException(status_code=404, detail="Agenda não encontrada.")

    dados_dict = dados.model_dump(exclude_unset=True)

    for campo, valor in dados_dict.items():
        setattr(agenda, campo, valor)

    db.commit()
    db.refresh(agenda)
    return agenda


def deletar_agenda(db: Session, agenda_id: int):
    #remove um horário da agenda
    agenda = get_agenda(db, agenda_id)

    if not agenda:
        raise HTTPException(status_code=404, detail="Agenda não encontrada.")

    db.delete(agenda)
    db.commit()
    return {"message": "Horário removido com sucesso."}
