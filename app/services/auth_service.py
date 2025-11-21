from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.usuario import Usuario
from app.services.usuario_service import verificar_senha
from app.core.security import criar_token_acesso


def autenticar_usuario(email: str, senha: str, db: Session):
    # Busca usuário pelo email
    usuario = db.query(Usuario).filter(Usuario.email == email).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos."
        )

    # Valida a senha
    if not verificar_senha(senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos."
        )

    # Gerar o token
    token = criar_token_acesso({"sub": str(usuario.id)})

    return token, usuario
