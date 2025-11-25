from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.profissional_saude import ProfissionalSaude
from app.models.usuario import Usuario

from app.schemas.profissional_schema import (
    ProfissionalCreate,
    ProfissionalUpdate
)


def criar_profissional_service(dados: ProfissionalCreate, db: Session) -> ProfissionalSaude:
    # Verificar se o usuário existe
    usuario = db.query(Usuario).filter(Usuario.id == dados.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    # Verificar se o usuário já é profissional
    existente = db.query(ProfissionalSaude).filter(
        ProfissionalSaude.usuario_id == dados.usuario_id
    ).first()
    if existente:
        raise HTTPException(status_code=400, detail="Este usuário já está vinculado a um profissional de saúde.")

    # Criar novo profissional
    profissional = ProfissionalSaude(
        usuario_id=dados.usuario_id,
        tipo_profissional=dados.tipo_profissional,
        registro_profissional=dados.registro_profissional
    )

    db.add(profissional)
    db.commit()
    db.refresh(profissional)
    return profissional


def buscar_profissional_por_id_service(profissional_id: int, db: Session):
    p = db.query(ProfissionalSaude).filter(
        ProfissionalSaude.id == profissional_id
    ).first()

    if not p:
        raise HTTPException(status_code=404, detail="Profissional não encontrado.")

    return {
        "id": p.id,
        "tipo_profissional": p.tipo_profissional,
        "registro_profissional": p.registro_profissional,
        "usuario": {
            "id": p.usuario.id,
            "nome": p.usuario.nome
        }
    }



def listar_profissionais_service(db: Session):
    profissionais = db.query(ProfissionalSaude).all()
    resultados = []

    for p in profissionais:
        resultados.append({
            "id": p.id,
            "tipo_profissional": p.tipo_profissional,
            "registro_profissional": p.registro_profissional,
            "usuario": {
                "id": p.usuario.id,
                "nome": p.usuario.nome
            }
        })

    return resultados



def atualizar_profissional_service(profissional_id: int, dados: ProfissionalUpdate, db: Session) -> ProfissionalSaude:
    profissional = db.query(ProfissionalSaude).filter(
        ProfissionalSaude.id == profissional_id
    ).first()

    if not profissional:
        raise HTTPException(status_code=404, detail="Profissional não encontrado.")

    dados_dict = dados.model_dump(exclude_unset=True)

    for campo, valor in dados_dict.items():
        setattr(profissional, campo, valor)

    db.commit()
    db.refresh(profissional)
    return profissional


def deletar_profissional_service(profissional_id: int, db: Session):
    profissional = db.query(ProfissionalSaude).filter(
        ProfissionalSaude.id == profissional_id
    ).first()

    if not profissional:
        raise HTTPException(status_code=404, detail="Profissional não encontrado.")

    db.delete(profissional)
    db.commit()
    return {"message": "Profissional deletado com sucesso."}
