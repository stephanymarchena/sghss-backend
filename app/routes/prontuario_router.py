from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.auth import get_current_user, is_admin

from app.schemas.prontuario_schema import (
    ProntuarioResponse,
    EntradaProntuarioCreate,
    EntradaProntuarioResponse
)

from app.services.prontuario_service import (
    criar_prontuario,
    get_prontuario_by_paciente_id,
    adicionar_entrada,
    listar_entradas
)

router = APIRouter(prefix="/prontuarios", tags=["Prontuários"])


# ---------------------------------------------------------
# Criar prontuário — SOMENTE ADMIN
# ---------------------------------------------------------
@router.post("/{paciente_id}", response_model=ProntuarioResponse, dependencies=[Depends(is_admin)])
def criar_prontuario_route(
    paciente_id: int,
    db: Session = Depends(get_db)
):
    prontuario = criar_prontuario(db, paciente_id)
    return ProntuarioResponse.model_validate(prontuario)


# ---------------------------------------------------------
# Ver prontuário — ADMIN, PROFISSIONAL DO PACIENTE, OU O PACIENTE
# ---------------------------------------------------------
@router.get("/{paciente_id}", response_model=ProntuarioResponse)
def obter_prontuario(
    paciente_id: int,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    prontuario = get_prontuario_by_paciente_id(db, paciente_id)

    # ADMIN pode tudo
    if usuario_atual.role == "admin":
        return ProntuarioResponse.model_validate(prontuario)

    # PACIENTE pode ver seu próprio prontuário
    if hasattr(usuario_atual, "paciente") and usuario_atual.paciente:
        if usuario_atual.paciente[0].id == paciente_id:
            return ProntuarioResponse.model_validate(prontuario)

    # PROFISSIONAL pode ver prontuário de pacientes atendidos por ele
    if hasattr(usuario_atual, "profissional_saude") and usuario_atual.profissional_saude:
        profissional_id = usuario_atual.profissional_saude[0].id

        # verifica se este profissional já teve consulta com o paciente
        houve_consulta = any(
            entrada.consulta and entrada.consulta.profissional_id == profissional_id
            for entrada in prontuario.entradas
        )
        if houve_consulta:
            return ProntuarioResponse.model_validate(prontuario)

    raise HTTPException(403, "Você não tem permissão para acessar este prontuário.")


# ---------------------------------------------------------
# Adicionar entrada — SOMENTE PROFISSIONAL OU ADMIN
# ---------------------------------------------------------
@router.post("/{paciente_id}/entradas", response_model=EntradaProntuarioResponse)
def adicionar_entrada_route(
    paciente_id: int,
    dados: EntradaProntuarioCreate,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    # Apenas profissionais ou admin
    if usuario_atual.role != "admin":
        if not hasattr(usuario_atual, "profissional_saude") or not usuario_atual.profissional_saude:
            raise HTTPException(403, "Apenas profissionais podem adicionar entradas ao prontuário.")

    entrada = adicionar_entrada(db, paciente_id, dados)
    return EntradaProntuarioResponse.model_validate(entrada)


# ---------------------------------------------------------
# Listar entradas — Mesmas regras de visualização
# ---------------------------------------------------------
@router.get("/{paciente_id}/entradas", response_model=list[EntradaProntuarioResponse])
def listar_entradas_route(
    paciente_id: int,
    db: Session = Depends(get_db),
    usuario_atual = Depends(get_current_user)
):
    prontuario = get_prontuario_by_paciente_id(db, paciente_id)

    # ADMIN pode
    if usuario_atual.role == "admin":
        pass

    # PACIENTE pode ver seu próprio prontuário
    elif hasattr(usuario_atual, "paciente") and usuario_atual.paciente:
        if usuario_atual.paciente[0].id != paciente_id:
            raise HTTPException(403, "Você não pode ver entradas de outro paciente.")

    # PROFISSIONAL pode ver se já atendeu o paciente
    elif hasattr(usuario_atual, "profissional_saude") and usuario_atual.profissional_saude:
        profissional_id = usuario_atual.profissional_saude[0].id
        houve_consulta = any(
            entrada.consulta and entrada.consulta.profissional_id == profissional_id
            for entrada in prontuario.entradas
        )
        if not houve_consulta:
            raise HTTPException(403, "Você não possui permissão para acessar este prontuário.")

    else:
        raise HTTPException(403, "Acesso não autorizado.")

    entradas = listar_entradas(db, paciente_id)
    return [EntradaProntuarioResponse.model_validate(e) for e in entradas]
