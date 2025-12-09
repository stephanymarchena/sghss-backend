from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.auth import get_current_user, is_admin

from app.schemas.exame_schema import (
    ExameCreate,
    ExameUpdate,
    ExameResponse
)

from app.services.exame_service import (
    criar_exame_service,
    listar_exames_service,
    buscar_exame_service,
    atualizar_exame_service
)

from app.models.exame import Exame

router = APIRouter(prefix="/exames", tags=["Exames"])


# ---------------------------------------------------------
# CRIAR EXAME — ADMIN ou PROFISSIONAL
# ---------------------------------------------------------
@router.post("/", response_model=ExameResponse)
def criar_exame(
    dados: ExameCreate,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):

    # Somente admin e profissionais podem criar exames
    if usuario_atual.role != "admin":
        if not hasattr(usuario_atual, "profissional_saude") or not usuario_atual.profissional_saude:
            raise HTTPException(403, "Apenas profissionais podem cadastrar exames.")

    exame = criar_exame_service(dados, db)
    return ExameResponse.model_validate(exame)


# ---------------------------------------------------------
# LISTAR EXAMES (com regras por papel)
# ---------------------------------------------------------
@router.get("/", response_model=list[ExameResponse])
def listar_exames(
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):

    # ADMIN → vê tudo
    if usuario_atual.role == "admin":
        exames = listar_exames_service(db)
        return [ExameResponse.model_validate(e) for e in exames]

    # PROFISSIONAL → vê exames de seus pacientes
    if hasattr(usuario_atual, "profissional_saude") and usuario_atual.profissional_saude:
        prof_id = usuario_atual.profissional_saude[0].id

        exames = (
            db.query(Exame)
            .join(Exame.paciente)
            .filter(Exame.profissional_id == prof_id)
            .all()
        )
        return [ExameResponse.model_validate(e) for e in exames]

    # PACIENTE → vê só os seus exames
    if hasattr(usuario_atual, "paciente") and usuario_atual.paciente:
        paciente_id = usuario_atual.paciente[0].id

        exames = (
            db.query(Exame)
            .filter(Exame.paciente_id == paciente_id)
            .all()
        )
        return [ExameResponse.model_validate(e) for e in exames]

    # Usuário comum → NÃO PODE
    raise HTTPException(403, "Apenas pacientes, profissionais e administradores podem visualizar exames.")


# ---------------------------------------------------------
# BUSCAR EXAME POR ID — regras detalhadas
# ---------------------------------------------------------
@router.get("/{exame_id}", response_model=ExameResponse)
def buscar_exame(
    exame_id: int,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):

    exame = buscar_exame_service(exame_id, db)

    # Admin → sempre pode
    if usuario_atual.role == "admin":
        return ExameResponse.model_validate(exame)

    # Profissional → só exames dos seus pacientes
    if hasattr(usuario_atual, "profissional_saude") and usuario_atual.profissional_saude:
        prof_id = usuario_atual.profissional_saude[0].id
        if exame.profissional_id != prof_id:
            raise HTTPException(403, "Você não pode ver exames de outros profissionais.")
        return ExameResponse.model_validate(exame)

    # Paciente → só seus próprios exames
    if hasattr(usuario_atual, "paciente") and usuario_atual.paciente:
        paciente_id = usuario_atual.paciente[0].id
        if exame.paciente_id != paciente_id:
            raise HTTPException(403, "Você só pode ver seus próprios exames.")
        return ExameResponse.model_validate(exame)

    raise HTTPException(403, "Acesso não autorizado.")


# ---------------------------------------------------------
# ATUALIZAR EXAME — somente admin ou profissional responsável
# ---------------------------------------------------------
@router.patch("/{exame_id}", response_model=ExameResponse)
def atualizar_exame(
    exame_id: int,
    dados: ExameUpdate,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):

    exame = buscar_exame_service(exame_id, db)

    # Admin → pode tudo
    if usuario_atual.role == "admin":
        exame = atualizar_exame_service(exame_id, dados, db)
        return ExameResponse.model_validate(exame)

    # Profissional → só seu próprio exame
    if hasattr(usuario_atual, "profissional_saude") and usuario_atual.profissional_saude:
        prof_id = usuario_atual.profissional_saude[0].id
        if exame.profissional_id != prof_id:
            raise HTTPException(403, "Você só pode atualizar exames que você mesmo cadastrou.")
        exame = atualizar_exame_service(exame_id, dados, db)
        return ExameResponse.model_validate(exame)

    raise HTTPException(403, "Somente administradores e profissionais podem atualizar exames.")
