from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.auth import get_current_user

from app.schemas.profissional_schema import (
    ProfissionalCreate,
    ProfissionalUpdate,
    ProfissionalResponse
)

from app.services.profissional_service import (
    criar_profissional_service,
    buscar_profissional_por_id_service,
    listar_profissionais_service,
    atualizar_profissional_service,
    deletar_profissional_service
)


router = APIRouter(
    prefix="/profissionais",
    tags=["Profissionais de Saúde"]
)


@router.post("/", response_model=ProfissionalResponse)
def criar_profissional(
    dados: ProfissionalCreate,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    profissional = criar_profissional_service(dados, db)
    return ProfissionalResponse.model_validate(profissional)


@router.get("/", response_model=list[ProfissionalResponse])
def listar_profissionais(
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    profissionais = listar_profissionais_service(db)
    return [ProfissionalResponse.model_validate(p) for p in profissionais]


@router.get("/{profissional_id}", response_model=ProfissionalResponse)
def obter_profissional(
    profissional_id: int,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    profissional = buscar_profissional_por_id_service(profissional_id, db)
    return ProfissionalResponse.model_validate(profissional)


@router.patch("/{profissional_id}", response_model=ProfissionalResponse)
def atualizar_profissional(
    profissional_id: int,
    dados: ProfissionalUpdate,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    profissional = atualizar_profissional_service(profissional_id, dados, db)
    return ProfissionalResponse.model_validate(profissional)


@router.delete("/{profissional_id}")
def deletar_profissional(
    profissional_id: int,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    return deletar_profissional_service(profissional_id, db)
