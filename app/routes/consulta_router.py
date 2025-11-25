from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.auth import get_current_user

from app.schemas.consulta_schema import (
    ConsultaCreate,
    ConsultaUpdate,
    ConsultaResponse
)

from app.services.consulta_service import (
    agendar_consulta_service,
    buscar_consulta_por_id_service,
    listar_consultas_service,
    atualizar_consulta_service,
    confirmar_consulta_service,
    cancelar_consulta_service,
    finalizar_consulta_service,
    deletar_consulta_service
)

router = APIRouter(prefix="/consultas", tags=["Consultas"])

@router.post("/", response_model=ConsultaResponse)
def agendar_consulta(dados: ConsultaCreate, db: Session = Depends(get_db), usuario_atual = Depends(get_current_user)):
    consulta = agendar_consulta_service(dados, db)
    return ConsultaResponse.model_validate(consulta)

@router.get("/", response_model=list[ConsultaResponse])
def listar_consultas(db: Session = Depends(get_db), usuario_atual = Depends(get_current_user)):
    consultas = listar_consultas_service(db)
    return [ConsultaResponse.model_validate(c) for c in consultas]

@router.get("/{consulta_id}", response_model=ConsultaResponse)
def obter_consulta(consulta_id: int, db: Session = Depends(get_db), usuario_atual = Depends(get_current_user)):
    consulta = buscar_consulta_por_id_service(consulta_id, db)
    return ConsultaResponse.model_validate(consulta)

@router.patch("/{consulta_id}", response_model=ConsultaResponse)
def atualizar_consulta(consulta_id: int, dados: ConsultaUpdate, db: Session = Depends(get_db), usuario_atual = Depends(get_current_user)):
    consulta = atualizar_consulta_service(consulta_id, dados, db)
    return ConsultaResponse.model_validate(consulta)

# métodos conceituais do diagrama
@router.patch("/{consulta_id}/confirmar", response_model=ConsultaResponse)
def confirmar_consulta(consulta_id: int, db: Session = Depends(get_db), usuario_atual = Depends(get_current_user)):
    consulta = confirmar_consulta_service(consulta_id, db)
    return ConsultaResponse.model_validate(consulta)

@router.patch("/{consulta_id}/cancelar", response_model=ConsultaResponse)
def cancelar_consulta(consulta_id: int, db: Session = Depends(get_db), usuario_atual = Depends(get_current_user)):
    consulta = cancelar_consulta_service(consulta_id, db)
    return ConsultaResponse.model_validate(consulta)

@router.patch("/{consulta_id}/finalizar", response_model=ConsultaResponse)
def finalizar_consulta(consulta_id: int, db: Session = Depends(get_db), usuario_atual = Depends(get_current_user)):
    consulta = finalizar_consulta_service(consulta_id, db)
    return ConsultaResponse.model_validate(consulta)

@router.delete("/{consulta_id}")
def deletar_consulta(consulta_id: int, db: Session = Depends(get_db), usuario_atual = Depends(get_current_user)):
    return deletar_consulta_service(consulta_id, db)
