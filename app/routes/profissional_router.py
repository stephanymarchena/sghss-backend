from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.auth import get_current_user, is_admin

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


# ---------------------------------------------------------
# CRIAR PROFISSIONAL — SOMENTE ADMIN
# ---------------------------------------------------------
@router.post("/", response_model=ProfissionalResponse, dependencies=[Depends(is_admin)])
def criar_profissional(
    dados: ProfissionalCreate,
    db: Session = Depends(get_db)
):
    profissional = criar_profissional_service(dados, db)
    return ProfissionalResponse.model_validate(profissional)


# ---------------------------------------------------------
# LISTAR PROFISSIONAIS — QUALQUER USUÁRIO AUTENTICADO
# (pacientes precisam ver para agendar)
# ---------------------------------------------------------
@router.get("/", response_model=list[ProfissionalResponse])
def listar_profissionais(
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    profissionais = listar_profissionais_service(db)
    return [ProfissionalResponse.model_validate(p) for p in profissionais]


# ---------------------------------------------------------
# BUSCAR PROFISSIONAL — QUALQUER AUTENTICADO
# ---------------------------------------------------------
@router.get("/{profissional_id}", response_model=ProfissionalResponse)
def obter_profissional(
    profissional_id: int,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    profissional = buscar_profissional_por_id_service(profissional_id, db)
    return ProfissionalResponse.model_validate(profissional)


# ---------------------------------------------------------
# ATUALIZAR PROFISSIONAL
# Admin → pode tudo
# Profissional → pode atualizar apenas a si mesmo
# ---------------------------------------------------------
@router.patch("/{profissional_id}", response_model=ProfissionalResponse)
def atualizar_profissional(
    profissional_id: int,
    dados: ProfissionalUpdate,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    # ADMIN
    if usuario_atual.role == "admin":
        profissional = atualizar_profissional_service(profissional_id, dados, db)
        return ProfissionalResponse.model_validate(profissional)

    # PROFISSIONAL (somente sua própria ficha)
    if hasattr(usuario_atual, "profissional_saude") and usuario_atual.profissional_saude:
        meu_prof_id = usuario_atual.profissional_saude[0].id
        if meu_prof_id != profissional_id:
            raise HTTPException(403, "Você só pode editar seu próprio cadastro profissional.")
        profissional = atualizar_profissional_service(profissional_id, dados, db)
        return ProfissionalResponse.model_validate(profissional)

    raise HTTPException(403, "Apenas administradores ou o próprio profissional podem editar este cadastro.")


# ---------------------------------------------------------
# DELETAR PROFISSIONAL — SOMENTE ADMIN
# ---------------------------------------------------------
@router.delete("/{profissional_id}", dependencies=[Depends(is_admin)])
def deletar_profissional(
    profissional_id: int,
    db: Session = Depends(get_db)
):
    return deletar_profissional_service(profissional_id, db)
