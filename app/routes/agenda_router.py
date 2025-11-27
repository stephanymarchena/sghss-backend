# app/routes/agenda_router.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.core.auth import get_current_user

from app.schemas.agenda_schema import (
    AgendaCreate,
    AgendaUpdate,
    AgendaResponse
)

from app.services.agenda_service import (
    create_agenda,
    listar_agenda_profissional,
    listar_disponiveis,
    reservar_horario,
    liberar_horario,
    atualizar_agenda,
    deletar_agenda,
    get_agenda
)

router = APIRouter(
    prefix="/agendas",
    tags=["Agendas"]
)

# ---------------------------------------------------------
# Criar horário (apenas profissional)
# ---------------------------------------------------------
@router.post("/", response_model=AgendaResponse)
def criar_agenda(
    dados: AgendaCreate,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    # Se o usuário atual for um profissional, só pode criar agenda para si
    # hasattr() = tem esse atributo, retorna true e false
    if hasattr(usuario_atual, "profissional_saude") and usuario_atual.profissional_saude:
        if usuario_atual.profissional_saude[0].id != dados.profissional_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você só pode criar horários para a sua própria agenda."
            )

    agenda = create_agenda(db, dados)
    return agenda


# ---------------------------------------------------------
# Listar horários de um profissional
# ---------------------------------------------------------
@router.get("/profissional/{profissional_id}", response_model=list[AgendaResponse])
def listar_agenda_por_profissional(
    profissional_id: int,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    return listar_agenda_profissional(db, profissional_id)


# ---------------------------------------------------------
# Listar horários disponíveis por data
# ---------------------------------------------------------
@router.get("/disponiveis/{profissional_id}", response_model=list[AgendaResponse])
def listar_disponiveis_por_data(
    profissional_id: int,
    data: str = Query(..., description="Data no formato YYYY-MM-DD"),
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    try:
        data_obj = datetime.strptime(data, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de data inválido.")

    return listar_disponiveis(db, profissional_id, data_obj)


# ---------------------------------------------------------
# Reservar horário
# ---------------------------------------------------------
@router.put("/reservar/{agenda_id}", response_model=AgendaResponse)
def reservar_um_horario(
    agenda_id: int,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    agenda = reservar_horario(db, agenda_id)
    return agenda


# ---------------------------------------------------------
# Liberar horário
# ---------------------------------------------------------
@router.put("/liberar/{agenda_id}", response_model=AgendaResponse)
def liberar_um_horario(
    agenda_id: int,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    agenda = liberar_horario(db, agenda_id)
    return agenda


# ---------------------------------------------------------
# Atualizar horário
# ---------------------------------------------------------
@router.patch("/{agenda_id}", response_model=AgendaResponse)
def atualizar_um_horario(
    agenda_id: int,
    dados: AgendaUpdate,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    agenda = get_agenda(db, agenda_id)

    if not agenda:
        raise HTTPException(status_code=404, detail="Agenda não encontrada.")

    # Apenas o profissional dono da agenda pode editar
    if hasattr(usuario_atual, "profissional_saude") and usuario_atual.profissional_saude:
        if usuario_atual.profissional_saude[0].id != agenda.profissional_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não pode editar horários de outro profissional."
            )

    return atualizar_agenda(db, agenda_id, dados)


# ---------------------------------------------------------
# Deletar horário
# ---------------------------------------------------------
@router.delete("/{agenda_id}")
def deletar_um_horario(
    agenda_id: int,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    agenda = get_agenda(db, agenda_id)

    if not agenda:
        raise HTTPException(status_code=404, detail="Horário não encontrado.")

    # Apenas o dono da agenda pode deletar
    if hasattr(usuario_atual, "profissional_saude") and usuario_atual.profissional_saude:
        if usuario_atual.profissional_saude[0].id != agenda.profissional_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não pode excluir horários de outro profissional."
            )

    return deletar_agenda(db, agenda_id)
