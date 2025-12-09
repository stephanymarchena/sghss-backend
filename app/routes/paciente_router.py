from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.auth import get_current_user, is_admin

from app.schemas.paciente_schema import (
    PacienteCreate,
    PacienteUpdate,
    PacienteResponse
)

from app.services.paciente_service import (
    criar_paciente_service,
    buscar_paciente_por_id_service,
    listar_pacientes_service,
    atualizar_paciente_service,
    deletar_paciente_service
)

router = APIRouter(
    prefix="/pacientes",
    tags=["Pacientes"]
)


# ---------------------------------------------------------
# CRIAR PACIENTE — SOMENTE ADMIN
# ---------------------------------------------------------
@router.post("/", response_model=PacienteResponse, dependencies=[Depends(is_admin)])
def criar_paciente(
    dados: PacienteCreate,
    db: Session = Depends(get_db)
):
    paciente = criar_paciente_service(dados, db)
    return PacienteResponse.model_validate(paciente)


# ---------------------------------------------------------
# BUSCAR UM PACIENTE — ADMIN OU O PRÓPRIO DONO
# ---------------------------------------------------------
@router.get("/{paciente_id}", response_model=PacienteResponse)
def obter_paciente(
    paciente_id: int,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    paciente = buscar_paciente_por_id_service(paciente_id, db)

    # Admin pode tudo
    if usuario_atual.role == "admin":
        return PacienteResponse.model_validate(paciente)

    # Paciente só pode ver o próprio registro
    if hasattr(usuario_atual, "paciente") and usuario_atual.paciente:
        if usuario_atual.paciente[0].id == paciente_id:
            return PacienteResponse.model_validate(paciente)

    raise HTTPException(403, "Você só pode visualizar seu próprio cadastro.")


# ---------------------------------------------------------
# LISTAR TODOS OS PACIENTES — SOMENTE ADMIN
# ---------------------------------------------------------
@router.get("/", response_model=list[PacienteResponse], dependencies=[Depends(is_admin)])
def listar_pacientes(
    db: Session = Depends(get_db)
):
    pacientes = listar_pacientes_service(db)
    return [PacienteResponse.model_validate(p) for p in pacientes]


# ---------------------------------------------------------
# ATUALIZAR PACIENTE — SOMENTE ADMIN
# ---------------------------------------------------------
@router.patch("/{paciente_id}", response_model=PacienteResponse, dependencies=[Depends(is_admin)])
def atualizar_paciente(
    paciente_id: int,
    dados: PacienteUpdate,
    db: Session = Depends(get_db)
):
    paciente = atualizar_paciente_service(paciente_id, dados, db)
    return PacienteResponse.model_validate(paciente)


# ---------------------------------------------------------
# DELETAR PACIENTE — SOMENTE ADMIN
# ---------------------------------------------------------
@router.delete("/{paciente_id}", dependencies=[Depends(is_admin)])
def deletar_paciente(
    paciente_id: int,
    db: Session = Depends(get_db)
):
    return deletar_paciente_service(paciente_id, db)
