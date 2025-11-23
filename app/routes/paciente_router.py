from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.auth import get_current_user

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


@router.post("/", response_model=PacienteResponse)
def criar_paciente(
    dados: PacienteCreate,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    paciente = criar_paciente_service(dados, db)
    return PacienteResponse.model_validate(paciente)


@router.get("/{paciente_id}", response_model=PacienteResponse)
def obter_paciente(
    paciente_id: int,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    paciente = buscar_paciente_por_id_service(paciente_id, db)
    return PacienteResponse.model_validate(paciente)


@router.get("/", response_model=list[PacienteResponse])
def listar_pacientes(
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    pacientes = listar_pacientes_service(db)
    return [PacienteResponse.model_validate(p) for p in pacientes]


@router.patch("/{paciente_id}", response_model=PacienteResponse)
def atualizar_paciente(
    paciente_id: int,
    dados: PacienteUpdate,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    paciente = atualizar_paciente_service(paciente_id, dados, db)
    return PacienteResponse.model_validate(paciente)


@router.delete("/{paciente_id}")
def deletar_paciente(
    paciente_id: int,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    return deletar_paciente_service(paciente_id, db)
