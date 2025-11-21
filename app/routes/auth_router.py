from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.auth_service import autenticar_usuario
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(
    prefix="/auth",
    tags=["Autenticação"]
)

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)): # OAuth2PasswordRequestForm >> padrão do fastAPI
    """
    Login com email e senha.
    Retorna um token de acesso JWT.
    """
    token, usuario = autenticar_usuario(form_data.username, form_data.password, db)

    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario_id": usuario.id,
        "email": usuario.email
    }
