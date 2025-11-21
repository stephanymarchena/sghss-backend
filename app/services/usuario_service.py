from sqlalchemy.orm import Session
from fastapi import HTTPException
from passlib.context import CryptContext

from app.models.usuario import Usuario
from app.schemas.usuario_schema import UsuarioCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def gerar_hash_senha(senha: str) -> str:
    return pwd_context.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    return pwd_context.verify(senha, senha_hash)


def criar_usuario_service(dados: UsuarioCreate, db: Session) -> Usuario:
    
    # Verificar email duplicado
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

    # Gerar hash da senha || revisar esse print
    print(">>> Valor recebido para senha:", dados.senha, type(dados.senha))
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

def buscar_usuario_por_id(usuario_id: int, db:Session):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado."
        )
        
    return usuario

#Listando  todos os usuarios com GET || com limite para não ficar pesado

def listar_usuarios_service(skip: int, limit: int, nome: str | None, db: Session):
    query = db.query(Usuario)

    if nome:
        query = query.filter(Usuario.nome.ilike(f"%{nome}%"))

    return query.offset(skip).limit(limit).all()


