from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.auth import get_current_user, is_admin

from app.schemas.consulta_schema import (
    ConsultaCreate,
    ConsultaUpdate,
    ConsultaResponse
)

from app.services.consulta_service import (
    agendar_consulta_service,
    buscar_consulta_por_id_service,
    listar_consultas_service,
    atualizar_consulta_service,
    confirmar_consulta_service,
    cancelar_consulta_service,
    finalizar_consulta_service,
    deletar_consulta_service
)

from app.models.consulta import Consulta

router = APIRouter(prefix="/consultas", tags=["Consultas"])


# ---------------------------------------------------------
# AGENDAR CONSULTA (todo paciente autenticado pode)
# ---------------------------------------------------------
@router.post("/", response_model=ConsultaResponse)
def agendar_consulta(
    dados: ConsultaCreate,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    # ADMIN pode agendar para qualquer paciente
    if usuario_atual.role == "admin":
        consulta = agendar_consulta_service(dados, db)
        return ConsultaResponse.model_validate(consulta)

    # PACIENTE só agenda para si
    if hasattr(usuario_atual, "paciente") and usuario_atual.paciente:
        paciente_id_logado = usuario_atual.paciente[0].id

        if dados.paciente_id != paciente_id_logado:
            raise HTTPException(
                status_code=403,
                detail="Você só pode agendar consultas para você mesmo."
            )

        consulta = agendar_consulta_service(dados, db)
        return ConsultaResponse.model_validate(consulta)

    # PROFISSIONAL e USUÁRIO comum não podem agendar consulta
    raise HTTPException(
        status_code=403,
        detail="Apenas pacientes autenticados podem agendar consultas."
    )

# ---------------------------------------------------------
# LISTAR CONSULTAS (restrições por papel)
# ---------------------------------------------------------
@router.get("/", response_model=list[ConsultaResponse])
def listar_consultas(
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    # ADMIN → vê tudo
    if usuario_atual.role == "admin":
        consultas = listar_consultas_service(db)
        return [ConsultaResponse.model_validate(c) for c in consultas]

    # PROFISSIONAL DE SAÚDE → vê apenas as consultas em que ele é o profissional
    if hasattr(usuario_atual, "profissional_saude") and usuario_atual.profissional_saude:
        profissional_id = usuario_atual.profissional_saude[0].id

        consultas = (
            db.query(Consulta)
            .filter(Consulta.profissional_id == profissional_id)
            .all()
        )
        return [ConsultaResponse.model_validate(c) for c in consultas]

    # PACIENTE → vê apenas as consultas dele
    if hasattr(usuario_atual, "paciente") and usuario_atual.paciente:
        paciente_id = usuario_atual.paciente[0].id

        consultas = (
            db.query(Consulta)
            .filter(Consulta.paciente_id == paciente_id)
            .all()
        )
        return [ConsultaResponse.model_validate(c) for c in consultas]

    # USUÁRIO COMUM → sem acesso
    raise HTTPException(
        status_code=403,
        detail="Apenas pacientes, profissionais ou administradores podem visualizar consultas."
    )


# ---------------------------------------------------------
# BUSCAR CONSULTA POR ID (com regra de permissão)
# ---------------------------------------------------------
@router.get("/{consulta_id}", response_model=ConsultaResponse)
def obter_consulta(
    consulta_id: int,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    consulta = buscar_consulta_por_id_service(consulta_id, db)

    # ADMIN → sempre pode
    if usuario_atual.role == "admin":
        return ConsultaResponse.model_validate(consulta)

    # PROFISSIONAL → só se a consulta for dele
    if hasattr(usuario_atual, "profissional_saude") and usuario_atual.profissional_saude:
        profissional_id = usuario_atual.profissional_saude[0].id
        if consulta["profissional"]["id"] != profissional_id:
            raise HTTPException(status_code=403, detail="Você não pode ver consultas de outros profissionais.")
        return ConsultaResponse.model_validate(consulta)

    # PACIENTE → só se a consulta for dele
    if hasattr(usuario_atual, "paciente") and usuario_atual.paciente:
        paciente_id = usuario_atual.paciente[0].id
        if consulta["paciente"]["id"] != paciente_id:
            raise HTTPException(status_code=403, detail="Você só pode ver suas próprias consultas.")
        return ConsultaResponse.model_validate(consulta)

    raise HTTPException(status_code=403, detail="Acesso não autorizado.")


# ---------------------------------------------------------
# ATUALIZAR CONSULTA (somente admin ou paciente dono)
# ---------------------------------------------------------
@router.patch("/{consulta_id}", response_model=ConsultaResponse)
def atualizar_consulta(
    consulta_id: int,
    dados: ConsultaUpdate,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    # ADMIN → pode tudo
    if usuario_atual.role == "admin":
        consulta = atualizar_consulta_service(consulta_id, dados, db)
        return ConsultaResponse.model_validate(consulta)

    # PACIENTE → só pode atualizar consulta dele
    if hasattr(usuario_atual, "paciente") and usuario_atual.paciente:
        paciente_id = usuario_atual.paciente[0].id

        consulta_existente = buscar_consulta_por_id_service(consulta_id, db)
        if consulta_existente["paciente"]["id"] != paciente_id:
            raise HTTPException(status_code=403, detail="Você só pode alterar suas próprias consultas.")

        consulta = atualizar_consulta_service(consulta_id, dados, db)
        return ConsultaResponse.model_validate(consulta)

    raise HTTPException(status_code=403, detail="Apenas pacientes e administradores podem atualizar consultas.")


# ---------------------------------------------------------
# CONFIRMAR CONSULTA (apenas profissional)
# ---------------------------------------------------------
@router.patch("/{consulta_id}/confirmar", response_model=ConsultaResponse)
def confirmar_consulta(
    consulta_id: int,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    # PROFISSIONAL → só se a consulta for dele
    if hasattr(usuario_atual, "profissional_saude") and usuario_atual.profissional_saude:
        profissional_id = usuario_atual.profissional_saude[0].id
        c = buscar_consulta_por_id_service(consulta_id, db)
        if c["profissional"]["id"] != profissional_id:
            raise HTTPException(status_code=403, detail="Você só pode confirmar consultas de sua agenda.")

        consulta = confirmar_consulta_service(consulta_id, db)
        return ConsultaResponse.model_validate(consulta)

    raise HTTPException(status_code=403, detail="Apenas profissionais podem confirmar consultas.")


# ---------------------------------------------------------
# CANCELAR CONSULTA (paciente dono, profissional dono, admin)
# ---------------------------------------------------------
@router.patch("/{consulta_id}/cancelar", response_model=ConsultaResponse)
def cancelar_consulta(
    consulta_id: int,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    c = buscar_consulta_por_id_service(consulta_id, db)

    # ADMIN → pode tudo
    if usuario_atual.role == "admin":
        return ConsultaResponse.model_validate(cancelar_consulta_service(consulta_id, db))

    # PROFISSIONAL → só se a consulta for dele
    if hasattr(usuario_atual, "profissional_saude") and usuario_atual.profissional_saude:
        profissional_id = usuario_atual.profissional_saude[0].id

        if c["profissional"]["id"] != profissional_id:
            raise HTTPException(status_code=403, detail="Você não pode cancelar consultas de outro profissional.")

        return ConsultaResponse.model_validate(cancelar_consulta_service(consulta_id, db))

    # PACIENTE → só se a consulta for dele
    if hasattr(usuario_atual, "paciente") and usuario_atual.paciente:
        paciente_id = usuario_atual.paciente[0].id

        if c["paciente"]["id"] != paciente_id:
            raise HTTPException(status_code=403, detail="Você só pode cancelar suas próprias consultas.")

        return ConsultaResponse.model_validate(cancelar_consulta_service(consulta_id, db))

    raise HTTPException(status_code=403, detail="Acesso negado.")


# ---------------------------------------------------------
# FINALIZAR CONSULTA (somente profissional)
# ---------------------------------------------------------
@router.patch("/{consulta_id}/finalizar", response_model=ConsultaResponse)
def finalizar_consulta(
    consulta_id: int,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    # PROFISSIONAL → só se a consulta for dele
    if hasattr(usuario_atual, "profissional_saude") and usuario_atual.profissional_saude:
        profissional_id = usuario_atual.profissional_saude[0].id

        c = buscar_consulta_por_id_service(consulta_id, db)
        if c["profissional"]["id"] != profissional_id:
            raise HTTPException(status_code=403, detail="Você não pode finalizar consultas de outro profissional.")

        return ConsultaResponse.model_validate(finalizar_consulta_service(consulta_id, db))

    raise HTTPException(status_code=403, detail="Apenas profissionais podem finalizar consultas.")


# ---------------------------------------------------------
# DELETAR CONSULTA (somente admin)
# ---------------------------------------------------------
@router.delete("/{consulta_id}", dependencies=[Depends(is_admin)])
def deletar_consulta(
    consulta_id: int,
    db: Session = Depends(get_db),
):
    return deletar_consulta_service(consulta_id, db)
