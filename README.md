


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


Dessa forma você só precisa rodar o arquivo com `"python povoar.py"` no terminal e ir direto testar!
Mais abaixo contém o corpo da requisão de alguns métodos para ajudar nos testes também (:


# 📌 Principais Rotas da API

**Obs.:** : As rotas possuem diferentes níveis de acesso. 

Para fins de teste, recomenda-se utilizar o usuário Administrador (Maria), que possui permissões mais amplas e permite explorar todos os módulos do sistema com menos restrições.

### 👤 Usuários
| Método | Endpoint      | Descrição                     |
|--------|---------------|-------------------------------|
| POST   | /usuarios     | Cadastro de usuário (sign up) |
| GET    | /usuarios/{id} | Lista usuario por id         |

Exemplo: Corpo da requisição para cadastro de usuário (sign up) - use com o método POST acima:

```bash
{
  "nome": "Tomas Machado",
  "cpf": "4786582531",
  "telefone": "2255847581",
  "endereco": "Av Brasil, 42000",
  "email": "tomas.paciente@sghss.com",
  "sexo": "Masculino",
  "data_nascimento": "1984-08-30",
  "senha": "senha123"
}
```

### 🔐 Autenticação
| Método | Endpoint    | Descrição      |
|--------|-------------|----------------|
| POST   | /auth/login | Gera token JWT |

Para autenticar use o x-www-form_urlcoded no postman com os dados do usuario, por exemplo:

```bash
{
  "email": "admin@email.com",
  "senha": "123456"
}

```


### 🧍 Pacientes
| Método | Endpoint     | Descrição          |
|--------|--------------|--------------------|
| POST   | /pacientes   | Criar paciente     |
| GET    | /pacientes   | Listar pacientes   |

Exemplo: Corpo da requisição para cadastrar um paciente com método POST, após cadastrar um usuario você pode transformá-lo em paciente conforme abaixo.

```bash
 {
  "usuario_id": {id_do_usuario}
}
```


### 🧑‍⚕️ Profissionais de Saúde
| Método | Endpoint                     | Descrição                         |
|--------|----------------------------- |---------------------------------- |
| POST   | /profissionais               | Criar profissional                |
| GET    | /profissionais               | Listar profissionais              |
| GET    | /agendas/profissional/{id}   | Listar horários dos profissionais |

Exemplo: Corpo da requisição para cadastrar um profissional de saúde com método POST:

```bash
{
  "usuario_id": {id},
  "tipo_profissional": "medico",
  "registro_profissional": "CRM-12345"
}
```

obs: tipos de profissonais permitidos: "medico", "enfermeiro", "tecnico"


### 📅 Consultas
| Método | Endpoint                       | Descrição                           |
|--------|--------------------------------|-------------------------------------|
| POST   | /consultas                     | Agendar consulta                    |
| PATCH  | /consultas/{id}/confirmar      | Confirmar consulta                  |
| PATCH  | /consultas/{id}/cancelar       | Cancelar consulta                   |
| PATCH  | /consultas/{id}/finalizar      | Finalizar consulta (gera prontuário)|
| PATCH  | /consultas/{id}                | Reagendar consulta                  |

Exemplo: corpo da requisição para reagendar consulta (altere para uma data futura se necessário):

```bash
{
  "data_hora": "2026-05-29T09:00:00"
}
```

### 🧪 Exames
| Método | Endpoint       | Descrição                       |
|--------|----------------|---------------------------------|
| POST   | /exames        | Registrar exame                 |
| PATCH  | /exames/{id}   | Atualizar status / resultado    |

Exemplo: corpo da requisição para registrar exame (mude os dados se necessário):

```bash
{
  "paciente_id": 1,
  "profissional_id": 2,
  "consulta_id": 10,
  "tipo_exame": "Texto"
}
```

Exemplo: Corpo da requisição para atualizar exames / resultado 

```bash
{
  "status": "Texto",
  "resultado": "Texto"
}
```

### 📝 Prontuário
| Método | Endpoint                   | Descrição                  |
|--------|----------------------------|----------------------------|
| GET    | /prontuarios/{paciente_id} | Ver histórico do paciente  |


### 🔔 Notificações
| Método | Endpoint                    | Descrição                            |
|--------|-----------------------------|--------------------------------------|
| GET    | /notificacoes               | Notificações do usuário autenticado  |
| POST   | /notificacoes/{usuario_id}  |Criação de notificação (Administrador)|

Exemplo: Corpo da requisição para criar notificações (Administrador) 

```bash
{
  "tipo": "Texto",
  "mensagem": "Texto"
}
```


### 📊 Relatórios
| Método | Endpoint                                | Descrição                  |
|--------|-----------------------------------------|----------------------------|
| GET    | /relatorios/consultas-por-status        | Consultas por status       |
| GET    | /relatorios/consultas-por-mes           | Consultas por mês          |
| GET    | /relatorios/consultas-por-profissional  | Consultas por profissional |


