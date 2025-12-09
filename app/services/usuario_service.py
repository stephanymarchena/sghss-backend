from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from passlib.context import CryptContext

from app.models.usuario import Usuario
from app.schemas.usuario_schema import UsuarioCreate, UsuarioUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------------------------------------------------
# FUNÇÕES DE SENHA
# ---------------------------------------------------------
def gerar_hash_senha(senha: str) -> str:
    return pwd_context.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    return pwd_context.verify(senha, senha_hash)


# ---------------------------------------------------------
# CRIAR USUÁRIO
# ---------------------------------------------------------
def criar_usuario_service(dados: UsuarioCreate, db: Session) -> Usuario:

    # Verificar e-mail duplicado
    usuario_existente_email = (
        db.query(Usuario).filter(Usuario.email == dados.email).first()
    )
    if usuario_existente_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="E-mail já está cadastrado."
        )

    # Verificar CPF duplicado
    usuario_existente_cpf = (
        db.query(Usuario).filter(Usuario.cpf == dados.cpf).first()
    )
    if usuario_existente_cpf:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF já está cadastrado."
        )

    # Gerar hash da senha 
    senha_hash = gerar_hash_senha(dados.senha)

    novo_usuario = Usuario(
        nome=dados.nome,
        cpf=dados.cpf,
        telefone=dados.telefone,
        endereco=dados.endereco,
        email=dados.email,
        sexo=dados.sexo,
        data_nascimento=dados.data_nascimento,
        senha_hash=senha_hash,
    )

    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    return novo_usuario


# ---------------------------------------------------------
# BUSCAR USUÁRIO POR ID
# ---------------------------------------------------------
def buscar_usuario_por_id(usuario_id: int, db: Session):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado."
        )

    return usuario


# ---------------------------------------------------------
# LISTAR USUÁRIOS
# ---------------------------------------------------------
def listar_usuarios_service(skip: int, limit: int, nome: str | None, db: Session):
    query = db.query(Usuario)

    if nome:
        query = query.filter(Usuario.nome.ilike(f"%{nome}%"))

    return query.offset(skip).limit(limit).all()


# ---------------------------------------------------------
# ATUALIZAR USUÁRIO (PATCH)
# ---------------------------------------------------------
def atualizar_usuario_service(usuario_id: int, dados: UsuarioUpdate, db: Session) -> Usuario:
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    dados_dict = dados.model_dump(exclude_unset=True)

    # Verificar e-mail duplicado
    if "email" in dados_dict:
        usuario_existente = db.query(Usuario).filter(
            Usuario.email == dados_dict["email"],
            Usuario.id != usuario_id
        ).first()

        if usuario_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="E-mail já está cadastrado."
            )

    # Se vier senha nova → gerar hash
    if "senha" in dados_dict:
        dados_dict["senha_hash"] = gerar_hash_senha(dados_dict.pop("senha"))

    # Atualizar campos dinamicamente
    for campo, valor in dados_dict.items():
        setattr(usuario, campo, valor)

    db.commit()
    db.refresh(usuario)
    return usuario


# ---------------------------------------------------------
# EXCLUSÃO FÍSICA
# ---------------------------------------------------------
def deletar_usuario_service(usuario_id: int, db: Session):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado."
        )

    db.delete(usuario)
    db.commit()
    return {"message": "Usuário deletado com sucesso."}
