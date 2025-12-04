from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.consulta import Consulta
from app.models.profissional_saude import ProfissionalSaude


# 1) Consultas por status
def consultas_por_status_service(db: Session):
    resultados = (
        db.query(Consulta.status, func.count(Consulta.id))
        .group_by(Consulta.status)
        .all()
    )

    return {
        "consultas_por_status": {
            status: quantidade for status, quantidade in resultados
        }
    }


# 2) Consultas por mês
def consultas_por_mes_service(db: Session):
    resultados = (
        db.query(
            func.strftime("%Y-%m", Consulta.data_hora).label("mes"),
            func.count(Consulta.id)
        )
        .group_by("mes")
        .order_by("mes")
        .all()
    )

    return {
        "consultas_por_mes": [
            {"mes": mes, "total": total}
            for mes, total in resultados
        ]
    }


# 3) Consultas por profissional
def consultas_por_profissional_service(db: Session):
    resultados = (
        db.query(
            ProfissionalSaude.id,
            ProfissionalSaude.tipo_profissional,
            func.count(Consulta.id)
        )
        .join(Consulta, Consulta.profissional_id == ProfissionalSaude.id)
        .group_by(ProfissionalSaude.id)
        .all()
    )

    return {
        "consultas_por_profissional": [
            {
                "profissional_id": prof_id,
                "tipo": tipo,
                "total_consultas": total
            }
            for prof_id, tipo, total in resultados
        ]
    }
