from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.auth import is_admin
from app.models.usuario import Usuario
from app.schemas.usuario_schema import UsuarioResponse

router = APIRouter(prefix="/admin", tags=["Admin"])


# LISTAR TODOS OS USUÁRIOS (somente admin)
@router.get("/usuarios", response_model=list[UsuarioResponse])
def listar_usuarios(db: Session = Depends(get_db), admin = Depends(is_admin)):
    usuarios = db.query(Usuario).all()
    return usuarios


# PROMOVER UM USUÁRIO A ADMIN
@router.patch("/promover/{usuario_id}", response_model=UsuarioResponse)
def promover_usuario_admin(
    usuario_id: int,
    db: Session = Depends(get_db),
    admin = Depends(is_admin)   # somente admin pode promover
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    usuario.role = "admin"
    db.commit()
    db.refresh(usuario)

    return usuario
