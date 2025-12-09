


# 🏥 SGHSS – Sistema de Gestão Hospitalar e Serviços de Saúde

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Framework-brightgreen)
![SQLAlchemy](https://img.shields.io/badge/ORM-SQLAlchemy-red)
![JWT](https://img.shields.io/badge/Auth-JWT-yellow)
![Status](https://img.shields.io/badge/Status-Concluído-success)
![License](https://img.shields.io/badge/License-MIT-lightgrey)


O SGHSS é um sistema Back-End desenvolvido em FastAPI para gerenciar operações clínicas essenciais, incluindo cadastro e autenticação de usuários, gestão de pacientes, profissionais de saúde, consultas, prontuários, exames, notificações e relatórios administrativos.

O objetivo deste projeto foi entregar um MVP funcional, modular e seguro, estruturado com boas práticas de organização de código, separação de responsabilidades e utilização de recursos modernos como JWT, SQLAlchemy, Pydantic, e arquitetura em camadas (models → schemas → services → routes).

Para testar a API, recomenda-se utilizar o Postman, pois sua interface facilita o envio de requisições autenticadas e o gerenciamento de tokens JWT utilizados no projeto.

Este sistema foi desenvolvido como parte da disciplina Projeto Final de Back-End do curso de Análise e Desenvolvimento de Sistemas – UNINTER.





## 📂 Estrutura da Aplicação

app/
 
 ├── core/          # Autenticação, segurança e configuração
 
 ├── models/        # Entidades do banco (SQLAlchemy)
 
 ├── schemas/       # Validação (Pydantic)
 
 ├── routes/        # Endpoints organizados por domínio
 
 ├── services/      # Regras de negócio
 
 ├── database.py    # Conexão e sessão com o banco

 └── main.py        # Entrada da aplicação



## 🛞 Como Rodar o Projeto

1. **Clonar o repositório**
   
```bash
git clone https://github.com/stephanymarchena/sghss-backend.git

```

```bash
cd sghss-backend
```

2. **Criar ambiente virtual:**
```bash  
python -m venv venv
```

3. **Ativar ambiente:**

   Windows:
```bash  
venv\Scripts\activate
```

4. **Instalar dependências:**
```bash  
pip install -r requirements.txt
```

5. **Executar a API:**
 ```bash  
uvicorn app.main:app --reload
```

6. **Acessar documentação:**
 ```bash  
http://localhost:8000/docs
```

# 📌 Criando Dados para Teste

O sistema inclui um script de inicialização que cria automaticamente usuários e dados essenciais:

```bash
python povoar.py
```

Esse arquivo quando você rodar ele no terminal vai criar os registros abaixo:

🛠 Administrador

- **email:** `maria.admin@sghss.com`
- **senha:** `senha123`

🧑‍⚕️ Profissional de Saúde

- **email:** `roberto.medico@sghss.com`
- **senha:** `senha123`

🧍 Paciente

- **email:** `carlos.paciente@sghss.com`
- **senha:** `senha123`

Além disso, o script gera:

- Agenda com horário disponível
- Consulta agendada
- Exame concluído
- Entrada automática no prontuário


Dessa forma você só precisa rodar o arquivo com `"python povoar.py"` no terminal e ir direto testar (:


# 📌 Principais Rotas da API

**Obs.:** : As rotas possuem diferentes níveis de acesso. 

Para fins de teste, recomenda-se utilizar o usuário Administrador (Maria), que possui permissões mais amplas e permite explorar todos os módulos do sistema com menos restrições.

### 🔐 Autenticação
| Método | Endpoint    | Descrição      |
|--------|-------------|----------------|
| POST   | /auth/login | Gera token JWT |

### 👤 Usuários
| Método | Endpoint      | Descrição                     |
|--------|---------------|-------------------------------|
| GET    | /usuarios/me  | Dados do usuário autenticado  |

### 🧍 Pacientes
| Método | Endpoint     | Descrição          |
|--------|--------------|--------------------|
| POST   | /pacientes   | Criar paciente     |
| GET    | /pacientes   | Listar pacientes   |

### 🧑‍⚕️ Profissionais de Saúde
| Método | Endpoint          | Descrição            |
|--------|-------------------|----------------------|
| POST   | /profissionais    | Criar profissional   |
| GET    | /profissionais    | Listar profissionais |

### 📅 Consultas
| Método | Endpoint                       | Descrição                           |
|--------|--------------------------------|-------------------------------------|
| POST   | /consultas                     | Agendar consulta                    |
| PATCH  | /consultas/{id}/confirmar      | Confirmar consulta                  |
| PATCH  | /consultas/{id}/cancelar       | Cancelar consulta                   |
| PATCH  | /consultas/{id}/finalizar      | Finalizar consulta (gera prontuário)|

### 🧪 Exames
| Método | Endpoint       | Descrição                       |
|--------|----------------|---------------------------------|
| POST   | /exames        | Registrar exame                 |
| PATCH  | /exames/{id}   | Atualizar status / resultado    |

### 📝 Prontuário
| Método | Endpoint                   | Descrição                  |
|--------|----------------------------|----------------------------|
| GET    | /prontuarios/{paciente_id} | Ver histórico do paciente  |

### 🔔 Notificações
| Método | Endpoint        | Descrição                          |
|--------|-----------------|------------------------------------|
| GET    | /notificacoes   | Notificações do usuário autenticado|

### 📊 Relatórios
| Método | Endpoint                                | Descrição                  |
|--------|-----------------------------------------|----------------------------|
| GET    | /relatorios/consultas_por_status        | Consultas por status       |
| GET    | /relatorios/consultas_por_mes           | Consultas por mês          |
| GET    | /relatorios/consultas_por_profissional  | Consultas por profissional |


