from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.auth import get_current_user, is_admin

from app.schemas.notificacao_schema import NotificacaoCreate, NotificacaoResponse
from app.services.notificacao_service import (
    criar_notificacao_service,
    listar_minhas_notificacoes_service,
    listar_minhas_notificacoes_nao_lidas_service,
    marcar_notificacao_lida_service
)

router = APIRouter(prefix="/notificacoes", tags=["Notificações"])


# ---------------------------------------------------------
# Criar notificação manual — SOMENTE ADMIN
# ---------------------------------------------------------
@router.post("/{usuario_id}", response_model=NotificacaoResponse)
def criar_notificacao(
    usuario_id: int,
    dados: NotificacaoCreate,
    db: Session = Depends(get_db),
    admin = Depends(is_admin)
):
    return criar_notificacao_service(usuario_id, dados, db)


# ---------------------------------------------------------
# Listar TODAS as notificações do usuário autenticado
# ---------------------------------------------------------
@router.get("/", response_model=list[NotificacaoResponse])
def listar_minhas_notificacoes(
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    return listar_minhas_notificacoes_service(usuario_atual.id, db)


# ---------------------------------------------------------
# Listar notificações NÃO LIDAS do usuário autenticado
# ---------------------------------------------------------
@router.get("/nao-lidas", response_model=list[NotificacaoResponse])
def listar_nao_lidas(
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    return listar_minhas_notificacoes_nao_lidas_service(usuario_atual.id, db)


# ---------------------------------------------------------
# Marcar uma notificação como lida (somente o dono pode)
# ---------------------------------------------------------
@router.patch("/{notificacao_id}/lida", response_model=NotificacaoResponse)
def marcar_notificacao_lida(
    notificacao_id: int,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    return marcar_notificacao_lida_service(notificacao_id, usuario_atual.id, db)
