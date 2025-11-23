from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.services.usuario_service import (
    criar_usuario_service, 
    buscar_usuario_por_id, 
    listar_usuarios_service
)

from app.database import get_db
from app.schemas.usuario_schema import UsuarioCreate, UsuarioResponse, UsuarioListResponse
from app.core.auth import get_current_user

from app.schemas.usuario_schema import UsuarioUpdate
from app.services.usuario_service import atualizar_usuario_service
from app.services.usuario_service import deletar_usuario_service

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)

@router.post("/", response_model=UsuarioResponse)
def criar_usuario(dados: UsuarioCreate, db: Session = Depends(get_db)):
    usuario = criar_usuario_service(dados, db)
    return UsuarioResponse.model_validate(usuario)



@router.get("/me")
def obter_meu_usuario(usuario = Depends(get_current_user)):
    return usuario


@router.get("/{usuario_id}", response_model=UsuarioResponse)
def obter_usuario_por_id(usuario_id: int, db:Session=Depends(get_db), usuario_atual = Depends(get_current_user)):
    usuario = buscar_usuario_por_id(usuario_id, db)
    return UsuarioResponse.model_validate(usuario)


@router.get("/", response_model=list[UsuarioListResponse])
def listar_usuarios(skip: int = 0, limit: int = 10, nome: str | None = None, 
                    db: Session=Depends(get_db), usuario_atual=Depends(get_current_user)):
    
    usuarios = listar_usuarios_service(skip, limit, nome, db)
    return usuarios



@router.patch("/{usuario_id}", response_model=UsuarioResponse)
def atualizar_usuario(
    usuario_id: int,
    dados: UsuarioUpdate,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    usuario = atualizar_usuario_service(usuario_id, dados, db)
    return UsuarioResponse.model_validate(usuario)


@router.delete("/{usuario_id}")
def deletar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    resultado = deletar_usuario_service(usuario_id, db)
    return resultado