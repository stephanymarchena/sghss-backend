from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.models.exame import Exame
from app.models.paciente import Paciente
from app.models.profissional_saude import ProfissionalSaude

from app.schemas.exame_schema import ExameCreate, ExameUpdate
from app.services.prontuario_service import adicionar_entrada
from app.schemas.prontuario_schema import EntradaProntuarioCreate


# Criar exame
def criar_exame_service(dados: ExameCreate, db: Session) -> Exame:
    paciente = db.query(Paciente).filter(Paciente.id == dados.paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")

    profissional = db.query(ProfissionalSaude).filter(ProfissionalSaude.id == dados.profissional_id).first()
    if not profissional:
        raise HTTPException(status_code=404, detail="Profissional solicitante não encontrado.")

    exame = Exame(
        paciente_id=dados.paciente_id,
        profissional_id=dados.profissional_id,
        consulta_id=dados.consulta_id,
        tipo_exame=dados.tipo_exame,
        status="solicitado"
    )

    db.add(exame)
    db.commit()
    db.refresh(exame)
    return exame


# Listar exames
def listar_exames_service(db: Session):
    return db.query(Exame).all()


# Buscar exame por ID
def buscar_exame_service(exame_id: int, db: Session) -> Exame:
    exame = db.query(Exame).filter(Exame.id == exame_id).first()
    if not exame:
        raise HTTPException(status_code=404, detail="Exame não encontrado.")
    return exame


# Atualizar exame (status ou resultado)
def atualizar_exame_service(exame_id: int, dados: ExameUpdate, db: Session) -> Exame:
    exame = buscar_exame_service(exame_id, db)

    dados_dict = dados.model_dump(exclude_unset=True)
    status_anterior = exame.status  # guardar status antes da atualização

    # aplicar alterações
    for campo, valor in dados_dict.items():
        setattr(exame, campo, valor)

    exame.atualizado_em = datetime.now(timezone.utc)
    db.commit()
    db.refresh(exame)

    # integração EXAME -> PRONTUÁRIO
    if exame.status == "concluido" and status_anterior != "concluido":
        texto = f"Resultado do exame {exame.tipo_exame}: {exame.resultado or 'sem resultado informado.'}"
        adicionar_entrada(
            db=db,
            paciente_id=exame.paciente_id,
            dados=EntradaProntuarioCreate(
                texto=texto,
                tipo="exame",
                consulta_id=exame.consulta_id
            )
        )

    return exame
