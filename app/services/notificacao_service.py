from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.notificacao import Notificacao
from app.schemas.notificacao_schema import NotificacaoCreate


# Criar notificação
def criar_notificacao_service(usuario_id: int, dados: NotificacaoCreate, db: Session):
    notif = Notificacao(
        usuario_id=usuario_id,
        tipo=dados.tipo,
        mensagem=dados.mensagem
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif


# Listar notificações do usuário atual
def listar_minhas_notificacoes_service(usuario_id: int, db: Session):
    return (
        db.query(Notificacao)
        .filter(Notificacao.usuario_id == usuario_id)
        .order_by(Notificacao.data_envio.desc())
        .all()
    )


def listar_minhas_notificacoes_nao_lidas_service(usuario_id: int, db: Session):
    return (
        db.query(Notificacao)
        .filter(Notificacao.usuario_id == usuario_id, Notificacao.lida == False)
        .order_by(Notificacao.data_envio.desc())
        .all()
    )


# Marcar como lida, Só o dono pode marcar como lida
def marcar_notificacao_lida_service(notificacao_id: int, usuario_id: int, db: Session):
    notif = db.query(Notificacao).filter(
        Notificacao.id == notificacao_id,
        Notificacao.usuario_id == usuario_id
    ).first()

    if not notif:
        raise HTTPException(status_code=404, detail="Notificação não encontrada.")

    notif.lida = True
    db.commit()
    db.refresh(notif)
    return notif
