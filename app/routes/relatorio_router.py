from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.auth import is_admin
from app.services.relatorio_service import (
    consultas_por_status_service,
    consultas_por_mes_service,
    consultas_por_profissional_service
)

router = APIRouter(prefix="/relatorios", tags=["Relatórios"])


@router.get("/consultas-por-status")
def consultas_por_status(db: Session = Depends(get_db), admin = Depends(is_admin)):
    return consultas_por_status_service(db)


@router.get("/consultas-por-mes")
def consultas_por_mes(db: Session = Depends(get_db), admin = Depends(is_admin)):
    return consultas_por_mes_service(db)


@router.get("/consultas-por-profissional")
def consultas_por_profissional(db: Session = Depends(get_db), admin = Depends(is_admin)):
    return consultas_por_profissional_service(db)
