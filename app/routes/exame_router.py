from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.auth import get_current_user

from app.schemas.exame_schema import (
    ExameCreate, ExameUpdate, ExameResponse
)
from app.services.exame_service import (
    criar_exame_service,
    listar_exames_service,
    buscar_exame_service,
    atualizar_exame_service
)

router = APIRouter(prefix="/exames", tags=["Exames"])


@router.post("/", response_model=ExameResponse)
def criar_exame(dados: ExameCreate, db: Session = Depends(get_db), usuario = Depends(get_current_user)):
    exame = criar_exame_service(dados, db)
    return ExameResponse.model_validate(exame)


@router.get("/", response_model=list[ExameResponse])
def listar_exames(db: Session = Depends(get_db), usuario = Depends(get_current_user)):
    exames = listar_exames_service(db)
    return [ExameResponse.model_validate(e) for e in exames]


@router.get("/{exame_id}", response_model=ExameResponse)
def buscar_exame(exame_id: int, db: Session = Depends(get_db), usuario = Depends(get_current_user)):
    exame = buscar_exame_service(exame_id, db)
    return ExameResponse.model_validate(exame)


@router.patch("/{exame_id}", response_model=ExameResponse)
def atualizar_exame(exame_id: int, dados: ExameUpdate, db: Session = Depends(get_db), usuario = Depends(get_current_user)):
    exame = atualizar_exame_service(exame_id, dados, db)
    return ExameResponse.model_validate(exame)
