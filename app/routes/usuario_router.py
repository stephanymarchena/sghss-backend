from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.services.usuario_service import criar_usuario_service


from app.database import get_db
from app.schemas.usuario_schema import UsuarioCreate, UsuarioResponse
from app.models.usuario import Usuario

router = APIRouter(
    prefix="/usuarios", #prefixo = /usuarios
    tags=["Usuarios"] # tag pra documentar
)


@router.post("/", response_model=UsuarioResponse)
def criar_usuario(dados: UsuarioCreate, db: Session = Depends(get_db)):
    usuario = criar_usuario_service(dados, db)
    return UsuarioResponse.model_validate(usuario)
