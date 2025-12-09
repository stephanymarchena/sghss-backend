from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.core.auth import get_current_user, is_admin, is_profissional

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
# Criar horário (apenas profissional ou admin)
# ---------------------------------------------------------
@router.post("/", response_model=AgendaResponse)
def criar_agenda(
    dados: AgendaCreate,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):

    # Só admin OU profissional podem criar agenda
    if usuario_atual.role != "admin":
        if not hasattr(usuario_atual, "profissional_saude") or not usuario_atual.profissional_saude:
            raise HTTPException(403, "Apenas profissionais podem criar horários.")

        # Profissional só cria agenda para si
        if usuario_atual.profissional_saude[0].id != dados.profissional_id:
            raise HTTPException(
                403,
                "Você só pode criar horários para a sua própria agenda."
            )

    agenda = create_agenda(db, dados)
    return agenda


# ---------------------------------------------------------
# Listar horários de um profissional
# Somente admin ou o próprio profissional
# ---------------------------------------------------------
@router.get("/profissional/{profissional_id}", response_model=list[AgendaResponse])
def listar_agenda_por_profissional(
    profissional_id: int,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):

    # Admin vê tudo
    if usuario_atual.role != "admin":

        # Usuário precisa ser profissional
        if not hasattr(usuario_atual, "profissional_saude") or not usuario_atual.profissional_saude:
            raise HTTPException(403, "Acesso restrito a profissionais.")

        # Tem que ser o dono da agenda
        if usuario_atual.profissional_saude[0].id != profissional_id:
            raise HTTPException(403, "Você só pode ver sua própria agenda.")

    return listar_agenda_profissional(db, profissional_id)


# ---------------------------------------------------------
# Listar horários disponíveis por data (ABERTO a todos)
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
        raise HTTPException(400, "Formato de data inválido.")

    return listar_disponiveis(db, profissional_id, data_obj)


# ---------------------------------------------------------
# Reservar horário manualmente (admin ou dono da agenda)
# ---------------------------------------------------------
@router.put("/reservar/{agenda_id}", response_model=AgendaResponse)
def reservar_um_horario(
    agenda_id: int,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    agenda = get_agenda(db, agenda_id)
    if not agenda:
        raise HTTPException(404, "Horário não encontrado.")

    # se não for admin → precisa ser dono
    if usuario_atual.role != "admin":
        if not hasattr(usuario_atual, "profissional_saude") or not usuario_atual.profissional_saude:
            raise HTTPException(403, "Apenas profissionais podem reservar horários.")
        if usuario_atual.profissional_saude[0].id != agenda.profissional_id:
            raise HTTPException(403, "Você só pode reservar horários da sua própria agenda.")

    return reservar_horario(db, agenda_id)


# ---------------------------------------------------------
# Liberar horário (admin ou dono)
# ---------------------------------------------------------
@router.put("/liberar/{agenda_id}", response_model=AgendaResponse)
def liberar_um_horario(
    agenda_id: int,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    agenda = get_agenda(db, agenda_id)
    if not agenda:
        raise HTTPException(404, "Horário não encontrado.")

    if usuario_atual.role != "admin":
        if not hasattr(usuario_atual, "profissional_saude") or not usuario_atual.profissional_saude:
            raise HTTPException(403, "Apenas profissionais podem liberar horários.")
        if usuario_atual.profissional_saude[0].id != agenda.profissional_id:
            raise HTTPException(403, "Você só pode liberar horários da sua própria agenda.")

    return liberar_horario(db, agenda_id)


# ---------------------------------------------------------
# Atualizar horário (apenas dono ou admin)
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
        raise HTTPException(404, "Agenda não encontrada.")

    # Admin pode editar tudo
    if usuario_atual.role != "admin":
        # precisa ser o profissional dono
        if not hasattr(usuario_atual, "profissional_saude") or not usuario_atual.profissional_saude:
            raise HTTPException(403, "Apenas profissionais podem editar horários.")
        if usuario_atual.profissional_saude[0].id != agenda.profissional_id:
            raise HTTPException(403, "Você só pode editar sua própria agenda.")

    return atualizar_agenda(db, agenda_id, dados)


# ---------------------------------------------------------
# Deletar horário (apenas dono ou admin)
# ---------------------------------------------------------
@router.delete("/{agenda_id}")
def deletar_um_horario(
    agenda_id: int,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    agenda = get_agenda(db, agenda_id)

    if not agenda:
        raise HTTPException(404, "Horário não encontrado.")

    if usuario_atual.role != "admin":
        if not hasattr(usuario_atual, "profissional_saude") or not usuario_atual.profissional_saude:
            raise HTTPException(403, "Apenas profissionais podem excluir horários.")
        if usuario_atual.profissional_saude[0].id != agenda.profissional_id:
            raise HTTPException(403, "Você só pode excluir horários da sua agenda.")

    return deletar_agenda(db, agenda_id)
