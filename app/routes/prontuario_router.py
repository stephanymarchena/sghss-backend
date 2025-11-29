from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.auth import get_current_user

from app.schemas.prontuario_schema import (
    ProntuarioResponse,
    EntradaProntuarioCreate,
    EntradaProntuarioResponse
)

from app.services.prontuario_service import (
    criar_prontuario,
    get_prontuario_by_paciente_id,
    adicionar_entrada,
    listar_entradas
)

router = APIRouter(prefix="/prontuarios", tags=["Prontuários"])


# ---------- Criar prontuário ----------
@router.post("/{paciente_id}", response_model=ProntuarioResponse)
def criar_prontuario_route(
    paciente_id: int,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    prontuario = criar_prontuario(db, paciente_id)
    return ProntuarioResponse.model_validate(prontuario)


# ---------- Buscar prontuário ----------
@router.get("/{paciente_id}", response_model=ProntuarioResponse)
def obter_prontuario(
    paciente_id: int,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    prontuario = get_prontuario_by_paciente_id(db, paciente_id)
    return ProntuarioResponse.model_validate(prontuario)


# ---------- Adicionar entrada ----------
@router.post("/{paciente_id}/entradas", response_model=EntradaProntuarioResponse)
def adicionar_entrada_route(
    paciente_id: int,
    dados: EntradaProntuarioCreate,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    entrada = adicionar_entrada(db, paciente_id, dados)
    return EntradaProntuarioResponse.model_validate(entrada)


# ---------- Listar entradas ----------
@router.get("/{paciente_id}/entradas", response_model=list[EntradaProntuarioResponse])
def listar_entradas_route(
    paciente_id: int,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    entradas = listar_entradas(db, paciente_id)
    return [EntradaProntuarioResponse.model_validate(e) for e in entradas]
