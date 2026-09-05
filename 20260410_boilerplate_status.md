# Boilerplate_v01 - Documentação Completa do Projeto

**Data**: 10 de Abril de 2026  
**Status**: Projeto Ativo - Fase 4 Entregue  
**Diretório**: `boilerplate_v01/`

---

## 1. Visão Geral do Projeto

### 1.1 Descrição

Boilerplate SaaS completo com **FastAPI + React**, arquitetura multi-tenant, sistema de billing ASAAS e emails transacionais via Brevo.Projeto de template para aplicações SaaS com todas as funcionalidades essenciais de autenticação, gerenciamento de organizações e cobrança.

### 1.2 Tecnologias Principais

| Componente | Tecnologia | Versão |
|------------|-------------|-------|
| Backend | FastAPI | 0.116 |
| Frontend | React | 19 |
| Database | PostgreSQL | 16 |
| Cache/Queue | Redis | 7 |
| Task Queue | Celery | 5.5 |
| ORM | SQLModel | 0.0.24 |
| Validação | Pydantic | 2.11 |
| Billing | ASAAS API | - |
| Email | Brevo | - |

---

## 2. Estrutura de Diretórios

```
boilerplate_v01/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/    # Endpoints da API
│   │   │   ├── auth.py
│   │   │   ├── billing.py
│   │   │   ├── organizations.py
│   │   │   ├── users.py
│   │   │   ├── core_feature.py
│   │   │   └── health.py
│   │   ├── core/               # Configurações centrais
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── security.py
│   │   │   ├── security_headers.py
│   │   │   ├── tenant.py
│   │   │   ├── limiter.py
│   │   │   └── cache.py
│   │   ├── models/            # Modelos do banco
│   │   │   ├── user.py
│   │   │   ├── organization.py
│   │   │   ├── subscription.py
│   │   │   ├── asaas_customer.py
│   │   │   ├── asaas_webhook_event.py
│   │   │   ├── email_delivery.py
│   │   │   ├── audit_log.py
│   │   │   └── feature_flag.py
│   │   ├── schemas/           # Schemas Pydantic
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   ├── organization.py
│   │   │   └── billing.py
│   │   ├── services/           # Lógica de negócio
│   │   │   ├── asaas_service.py
│   │   │   ├── email_service.py
│   │   │   ├── audit_service.py
│   │   │   └── feature_flag_service.py
│   │   ├── crud/              # Operações de banco
│   │   │   ├── user.py
│   │   │   ├── organization.py
│   │   │   └── subscription.py
│   │   └── background/
│   │       └── tasks.py        # Tarefas Celery
│   ├── tests/                 # Testes pytest
│   │   ├── test_auth.py
│   │   ├── test_users.py
│   │   ├── test_organizations.py
│   │   ├── test_billing.py
│   │   ├── test_security_headers.py
│   │   ├── test_auth_rate_limit.py
│   │   └── test_e2e.py
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── app/              # Páginas React
│   │   │   ├── page.tsx
│   │   │   ├── dashboard/
│   │   │   ├── billing/
│   │   │   ├── organizations/
│   │   │   └── auth/
│   │   ├── components/
│   │   │   ├── ui/           # Componentes UI
│   │   │   ├── layout/       # Layout (Sidebar, Header)
│   │   │   └── auth/         # Componentes auth
│   │   ├── hooks/            # Custom hooks
│   │   ├── store/           # Zustand stores
│   │   ├── lib/             # utilities
│   │   ├── types/          # TypeScript types
│   │   └── constants/      # Constantes
│   ├── tests/e2e/          # Testes Playwright
│   ├── package.json
│   └── vite.config.ts
├── infra/
│   └── scripts/
│       └── seed_db.py        # Script de seed
├── docker-compose.yml     # Produção
├── docker-compose.dev.yml # Desenvolvimento
├── render.yaml            # Deploy Render
├── Makefile              # Comandos
└── README.md
```

---

## 3. Configurações de Ambiente

### 3.1 Variáveis de Ambiente (.env)

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/saas_db

# Redis
REDIS_PASSWORD=dev-redis-password
REDIS_URL=redis://:dev-redis-password@localhost:6379/0

# JWT
JWT_SECRET_KEY=dev-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ASAAS (Billing)
ASAAS_API_KEY=
ASAAS_WEBHOOK_SECRET=
ASAAS_ENVIRONMENT=sandbox

# Brevo (Email)
BREVO_API_KEY=
BREVO_SENDER_EMAIL=noreply@example.com
BREVO_SENDER_NAME=SaaS Boilerplate
BREVO_TEMPLATE_WELCOME_ID=0
BREVO_TEMPLATE_RESET_ID=0
BREVO_TEMPLATE_INVITE_ID=0

# CORS & Security
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
ALLOWED_HOSTS=localhost,127.0.0.1

# Geral
PROJECT_NAME=SaaS Boilerplate
DEBUG=True
SENTRY_DSN=
```

---

## 4. Funcionalidades Implementadas

### 4.1 Fase 1: Base Backend

- [x] FastAPI com estrutura modular
- [x] PostgreSQL com SQLModel e Alembic
- [x] Autenticação JWT (access + refresh tokens)
- [x] CRUD de usuários e organizações
- [x] Arquitetura multi-tenant com middleware
- [x] Redis para cache e rate limiting

### 4.2 Fase 2: Autenticação & Multi-tenant

- [x] Fluxo completo: register → login → logout
- [x] Reset de senha via email
- [x] Refresh token com rotação
- [x] Tenant isolation middleware
- [x] Seed de dados inicial

### 4.3 Fase 3: Frontend de Produção

- [x] React 19 com React Hook Form + Zod
- [x] Estados de loading/erro com feedback via toast (sonner)
- [x] Rotas protegidas com fluxo de sessão
- [x] Telas de billing e organizações conectadas à API
- [x] Sidebar e header com navegação
- [x] TenantSwitch para alternar organizações

### 4.4 Fase 4: Segurança, Qualidade e Operação

#### Segurança
- [x] Rate limit global e por endpoint de auth
- [x] Proteção anti brute-force
- [x] Auditoria de eventos críticos
- [x] Hardening de headers HTTP (CSP, X-Frame-Options, nosniff)
- [x] CORS refinado (origens/métodos/headers explícitos)

#### Qualidade/CI
- [x] CI frontend: install → lint → build
- [x] CI backend: install → type-check → tests
- [x] Testes expandidos para segurança e auth

#### Operação
- [x] Docker Compose para produção e desenvolvimento
- [x] Makefile para comandos rápidos
- [x] Documentação de operações

---

## 5. Modelos de Dados

### 5.1 Organization

| Campo | Tipo | Descrição |
|-------|------|----------|
| id | UUID | Identificador |
| name | str | Nome da organização |
| created_at | datetime | Data de criação |
| updated_at | datetime | Data de atualização |

### 5.2 User

| Campo | Tipo | Descrição |
|-------|------|----------|
| id | UUID | Identificador |
| email | str | Email único |
| full_name | str | Nome completo |
| hashed_password | str | Senha hasheada |
| organization_id | UUID | FK para Organization |
| role | str | Papel (admin/member) |
| is_active | bool | Usuário ativo |
| email_verified | bool | Email verificado |
| reset_password_token | str | Token reset |
| refresh_token_version | int | Versão do refresh token |
| last_login_at | datetime | Último login |

### 5.3 Subscription (ASAAS)

| Campo | Tipo | Descrição |
|-------|------|----------|
| id | UUID | Identificador |
| organization_id | UUID | FK para Organization |
| asaas_subscription_id | str | ID no ASAAS |
| status | str | Status da assinatura |
| plan | str | Plano contratado |
| next_billing_date | date | Próxima cobrança |

### 5.4 AsaasCustomer

| Campo | Tipo | Descrição |
|-------|------|----------|
| id | UUID | Identificador |
| organization_id | UUID | FK para Organization |
| asaas_customer_id | str | ID no ASAAS |
| asaas_customer_email | str | Email no ASAAS |

---

## 6. Endpoints da API

### 6.1 Autenticação (`/api/v1/auth`)

| Método | Endpoint | Descrição |
|--------|----------|----------|
| POST | /register | Cadastro de usuário |
| POST | /login | Login (retorna tokens) |
| POST | /logout | Logout (invalida token) |
| POST | /refresh | Refresh token |
| POST | /reset-password | Solicita reset |
| POST | /reset-password/confirm | Confirma reset |

### 6.2 Organizações (`/api/v1/organizations`)

| Método | Endpoint | Descrição |
|--------|----------|----------|
| GET | / | Lista organizações |
| POST | / | Cria organização |
| GET | /{id} | Detalhes organização |
| PUT | /{id} | Atualiza organização |
| DELETE | /{id} | Remove organização |

### 6.3 Billing (`/api/v1/billing`)

| Método | Endpoint | Descrição |
|--------|----------|----------|
| GET | /subscription | Assinatura atual |
| POST | /checkout | Cria sessão de checkout |
| POST | /portal | Portal do cliente ASAAS |
| POST | /webhook | Webhook ASAAS |

### 6.4 Usuários (`/api/v1/users`)

| Método | Endpoint | Descrição |
|--------|----------|----------|
| GET | /me | Usuário atual |
| PUT | /me | Atualiza perfil |

### 6.5 Sistema

| Método | Endpoint | Descrição |
|--------|----------|----------|
| GET | /health | Health check |
| GET | /features | Feature flags |

---

## 7. Frontend - Estrutura de Páginas

### 7.1 Rotas

| Rota | Componente | Proteção |
|------|-----------|----------|
| / | LandingPage | Público |
| /auth/login | LoginPage | Público |
| /auth/register | RegisterPage | Público |
| /auth/reset-password | ResetPasswordPage | Público |
| /dashboard | DashboardPage | Autenticado |
| /billing | BillingPage | Autenticado |
| /organizations | OrganizationsPage | Autenticado |

### 7.2 Componentes Principais

- **UI Components**: Button, Input, Card
- **Layout Components**: Sidebar, Header, TenantSwitch
- **Auth Components**: ProtectedRoute

### 7.3 Estado Global (Zustand)

- **authStore**: Token, user, tenant, login/logout
- **tenantStore**: Organização atual, switch de tenant

### 7.4 Integrações

- **React Query**: Gerenciamento de estado de servidor
- **React Hook Form + Zod**: Validação de formulários
- **Axios**: Cliente HTTP com interceptors
- **Sonner**: Notificações toast

---

## 8. Comandos de Execução

### 8.1 Comandos Makefile

```bash
# Iniciar todos os serviços
make up

# Parar todos os serviços
make down

# Executar migrações
make migrate

# Seed do banco de dados
make seed

# Executar testes backend
make test-backend

# Desenvolvimento frontend
make frontend-dev

# Bootstrap completo
make bootstrap
```

### 8.2 Docker Compose

```bash
# Produção
docker compose up -d --build

# Desenvolvimento
docker compose -f docker-compose.dev.yml up -d --build
```

### 8.3 Frontend

```bash
cd frontend
npm run dev      # Desenvolvimento
npm run build   # Build produção
npm run lint    # Lint TypeScript
npm run test:e2e # Testes E2E
```

### 8.4 Backend

```bash
cd backend
poetry install    # Instalar dependências
poetry run uvicorn app.main:app --reload  # Desenvolvimento
poetry run pytest -v --cov=app          # Testes
poetry run alembic upgrade head          # Migrações
```

---

## 9. Integrações Externas

### 9.1 ASAAS (Billing)

- API de cobranças via `asaas-python`
- Webhooks para atualização de status
- Portal de cliente integrado
- Checkout transparente

### 9.2 Brevo (Email)

- API transaccional via `brevo-python`
- Templates: Welcome, Reset Password, Invite
- Tracking de entrega

### 9.3 Sentry (Monitoramento)

- Error tracking integrado
- Performance monitoring
- Tracing distribuído

### 9.4 OpenTelemetry

- Tracing distribuído
- Métricas customizadas

---

## 10. Testes

### 10.1 Backend (pytest)

| Arquivo | Cobertura |
|---------|-----------|
| test_auth.py | Autenticação completa |
| test_users.py | CRUD de usuários |
| test_organizations.py | CRUD de organizações |
| test_billing.py | Integração ASAAS |
| test_security_headers.py | Headers de segurança |
| test_auth_rate_limit.py | Rate limiting |
| test_e2e.py | Testes end-to-end |

### 10.2 Frontend (Playwright)

| Arquivo | Cobertura |
|---------|-----------|
| auth.spec.ts | Fluxo de autenticação |
| dashboard.spec.ts | Página inicial |
| billing.spec.ts | Billing e checkout |

---

## 11. Configuração de Deploy

### 11.1 Docker Compose (Produção)

Serviços:
- `postgres`: PostgreSQL 16
- `redis`: Redis 7
- `backend`: API FastAPI
- `celery-worker`: Worker Celery
- `celery-beat`: Agendador Celery
- `frontend`: Aplicação React

### 11.2 Render.com

Arquivo: `render.yaml` (configuração vazia - precisa configuração)

---

## 12._status Atual do Projeto

### 12.1 Completo

- Backend FastAPI com todas as APIs documentadas
- Frontend React com UI completa
- Sistema de autenticação multi-tenant
- Integração ASAAS (billing)
- Integração Brevo (email)
- Testes backend e e2e frontend
- Docker Compose para produção e desenvolvimento
- Makefile com comandos úteis

### 12.2 Pendente/Ajustar

- Configuração de deploy em produção (render.yaml vazio)
- Documentação de operação detalhada (docs/OPERATIONS.md não encontrado)
- Feature flags concretas para funcionalidades

### 12.3 Versão

- Backend: 0.1.0
- Frontend: 0.1.0

---

## 13. Referências

- Arquivo principal: `boilerplate_v01/README.md`
- Makefile: `boilerplate_v01/Makefile`
- Docker Compose: `boilerplate_v01/docker-compose.yml`
- pyproject.toml: `boilerplate_v01/backend/pyproject.toml`
- package.json: `boilerplate_v01/frontend/package.json`