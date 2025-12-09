# povoar.py — Script simples e seguro para povoamento inicial do SGHSS

from datetime import datetime, timezone
from app.database import SessionLocal, inicializar_bd

# Importar TODOS os modelos antes de usá-los (evita erro de mapeamento)
from app.models.usuario import Usuario
from app.models.paciente import Paciente
from app.models.profissional_saude import ProfissionalSaude
from app.models.prontuario import Prontuario
from app.models.entrada_prontuario import EntradaProntuario
from app.models.agenda import Agenda
from app.models.consulta import Consulta
from app.models.exame import Exame

from app.services.usuario_service import gerar_hash_senha


print("🔄 Inicializando banco...")
inicializar_bd()
db = SessionLocal()

try:
    print("📌 Criando ADMIN...")

    admin = Usuario(
        nome="Maria Oliveira",
        cpf="00000000000",
        telefone="11999990001",
        endereco="Rua Central, 100",
        email="maria.admin@sghss.com",
        senha_hash=gerar_hash_senha("senha123"),
        role="admin",
        sexo="feminino"
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)

    print("📌 Criando PACIENTE...")

    carlos = Usuario(
        nome="Carlos da Silva",
        cpf="11111111111",
        telefone="11999990002",
        endereco="Rua dos Lírios, 45",
        email="carlos.paciente@sghss.com",
        senha_hash=gerar_hash_senha("senha123"),
        sexo="masculino"
    )
    db.add(carlos)
    db.commit()
    db.refresh(carlos)

    paciente = Paciente(usuario_id=carlos.id)
    db.add(paciente)
    db.commit()
    db.refresh(paciente)

    prontuario = Prontuario(paciente_id=paciente.id)
    db.add(prontuario)
    db.commit()

    print("📌 Criando PROFISSIONAL...")
    roberto = Usuario(
        nome="Dr. Roberto Medeiros",
        cpf="22222222222",
        telefone="11999990003",
        endereco="Avenida Paulista, 800",
        email="roberto.medico@sghss.com",
        senha_hash=gerar_hash_senha("senha123"),
        sexo="masculino"
    )
    db.add(roberto)
    db.commit()
    db.refresh(roberto)

    prof = ProfissionalSaude(
        usuario_id=roberto.id,
        tipo_profissional="medico",
        registro_profissional="CRM123456"   # <-- ADICIONADO
    )
    db.add(prof)
    db.commit()
    db.refresh(prof)

    print("📌 Criando AGENDA...")

    agenda1 = Agenda(
        profissional_id=prof.id,
        data=datetime(2025, 12, 20).date(),
        hora=datetime(2025, 12, 20, 10, 0).time(),
        disponivel=True
    )
    db.add(agenda1)
    db.commit()
    db.refresh(agenda1)

    print("📌 Criando CONSULTA...")

    consulta = Consulta(
        paciente_id=paciente.id,
        profissional_id=prof.id,
        data_hora=datetime(2025, 12, 20, 10, 0, tzinfo=timezone.utc),
        status="agendada",
        observacoes="Primeira consulta"
    )
    db.add(consulta)

    # Marcar horário como reservado
    agenda1.disponivel = False
    db.commit()
    db.refresh(consulta)

    print("📌 Criando EXAME CONCLUÍDO...")

    exame = Exame(
        paciente_id=paciente.id,
        profissional_id=prof.id,
        consulta_id=consulta.id,
        tipo_exame="Hemograma",
        status="concluido",
        resultado="Exame normal, sem alterações.",
        atualizado_em=datetime.now(timezone.utc)
    )
    db.add(exame)
    db.commit()
    db.refresh(exame)

    print("\n🎉  POÇO DE SAÚDE POVOADO COM SUCESSO!")
    print("➡️  Admin: maria.admin@sghss.com / senha123")
    print("➡️  Paciente: carlos.paciente@sghss.com / senha123")
    print("➡️  Médico: roberto.medico@sghss.com / senha123")

except Exception as e:
    print("\n❌ ERRO DURANTE O POVOAMENTO:")
    print(str(e))

finally:
    db.close()
    print("🔒 Conexão fechada.")
