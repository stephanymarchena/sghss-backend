from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.services.usuario_service import (
    criar_usuario_service, 
    buscar_usuario_por_id, 
    listar_usuarios_service,
    atualizar_usuario_service,
    deletar_usuario_service
)

from app.database import get_db
from app.schemas.usuario_schema import UsuarioCreate, UsuarioResponse, UsuarioListResponse, UsuarioUpdate
from app.core.auth import get_current_user, is_admin

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)

# ---------------------------------------------------------
# CRIAR USUÁRIO SIGNUP
# ---------------------------------------------------------
@router.post("/", response_model=UsuarioResponse)
def criar_usuario(dados: UsuarioCreate, db: Session = Depends(get_db)):
    usuario = criar_usuario_service(dados, db)
    return UsuarioResponse.model_validate(usuario)


# ---------------------------------------------------------
# OBTER MEU PRÓPRIO USUÁRIO
# ---------------------------------------------------------
@router.get("/me", response_model=UsuarioResponse)
def obter_meu_usuario(usuario = Depends(get_current_user)):
    return UsuarioResponse.model_validate(usuario)


# ---------------------------------------------------------
# BUSCAR USUÁRIO POR ID
# admin pode ver qualquer um
# usuário normal só pode ver a si mesmo
# ---------------------------------------------------------
@router.get("/{usuario_id}", response_model=UsuarioResponse)
def obter_usuario_por_id(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    if usuario_atual.role != "admin" and usuario_atual.id != usuario_id:
        raise HTTPException(status_code=403, detail="Acesso negado.")

    usuario = buscar_usuario_por_id(usuario_id, db)
    return UsuarioResponse.model_validate(usuario)


# ---------------------------------------------------------
# LISTAR TODOS USUÁRIOS — SOMENTE ADMIN
# ---------------------------------------------------------
@router.get("/", response_model=list[UsuarioListResponse], dependencies=[Depends(is_admin)])
def listar_usuarios(
    skip: int = 0,
    limit: int = 10,
    nome: str | None = None,
    db: Session = Depends(get_db),
):
    return listar_usuarios_service(skip, limit, nome, db)


# ---------------------------------------------------------
# ATUALIZAR USUÁRIO
# admin pode atualizar qualquer usuário
# usuário comum só pode atualizar a si mesmo
# ---------------------------------------------------------
@router.patch("/{usuario_id}", response_model=UsuarioResponse)
def atualizar_usuario(
    usuario_id: int,
    dados: UsuarioUpdate,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    if usuario_atual.role != "admin" and usuario_atual.id != usuario_id:
        raise HTTPException(status_code=403, detail="Você só pode atualizar seu próprio perfil.")

    usuario = atualizar_usuario_service(usuario_id, dados, db)
    return UsuarioResponse.model_validate(usuario)


# ---------------------------------------------------------
# DELETAR USUÁRIO — SOMENTE ADMIN
# ---------------------------------------------------------
@router.delete("/{usuario_id}", dependencies=[Depends(is_admin)])
def deletar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
):
    return deletar_usuario_service(usuario_id, db)
