# IMPLEMENTATION_PLAN.md - 12 Prompts Sequenciais para Execução com IA

**Versão:** 2026.1 | **Projeto:** saas-boilerplate | **Stack:** FastAPI + React  
**Billing:** ASAAS | **Email:** Brevo | **IDE:** Agnóstico (Cursor, Windsurf, ClaudeCode, etc.)

---

## 📋 Como Usar Este Plano

### Instruções Gerais

```markdown
1. Execute os prompts EM ORDEM (Prompt 1 → Prompt 12)
2. Não pule etapas - cada prompt depende do anterior
3. Após cada prompt, faça git commit com mensagem descritiva
4. Valide com os comandos indicados antes de prosseguir
5. Se houver erro, corrija antes de avançar para o próximo prompt
```

### Fluxo de Trabalho Recomendado

```markdown
Para cada prompt:
1. Copie o prompt completo para o chat da IDE
2. Aguarde a IA gerar todos os arquivos
3. Execute os comandos de validação indicados
4. Faça git commit: git commit -m "feat: Prompt X - [tema]"
5. Revise visualmente os arquivos críticos
6. Avance para o próximo prompt
```

### Estimativa de Tempo

```yaml
Prompt 1-3: 30-45 minutos (estrutura + backend base)
Prompt 4-6: 45-60 minutos (backend completo + testes)
Prompt 7-9: 45-60 minutos (frontend + integração)
Prompt 10-12: 30-45 minutos (deploy + documentação)
Total estimado: 2.5 - 3.5 horas (com validações)
```

---

## 🎯 PROMPT 1 – Inicialização da Estrutura Completa do Projeto

**Tema:** Estrutura de diretórios + arquivos da raiz  
**Dependências:** Nenhuma (primeiro prompt)  
**Tempo estimado:** 15-20 minutos

```markdown
Você é um engenheiro sênior de software especializado em boilerplates SaaS.

Crie do zero a estrutura completa do projeto **saas-boilerplate** seguindo exatamente a árvore de diretórios abaixo.

**Árvore de diretórios completa a ser criada:**

saas-boilerplate/
├── .env.example
├── .gitignore
├── README.md
├── Makefile
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
├── .github/
│   └── workflows/
│        ├── ci-backend.yml
│        ├── ci-frontend.yml
│       └── deploy.yml
├── backend/
│    ├── pyproject.toml
│    ├── alembic.ini
│    ├── app/
│   │    ├── __init__.py
│   │    ├── main.py
│   │    ├── core/
│   │    ├── api/
│   │    ├── models/
│   │    ├── schemas/
│   │    ├── crud/
│   │    ├── services/
│   │    ├── utils/
│   │   └── background/
│    ├── alembic/
│   └── tests/
├── frontend/
│    ├── package.json
│    ├── vite.config.ts
│    ├── tsconfig.json
│    ├── tailwind.config.ts
│    ├── postcss.config.js
│    ├── eslint.config.js
│    ├── .env.example
│    ├── public/
│   └── src/
├── infra/
│   └── scripts/
└── docs/

**Instruções obrigatórias:**

1. Crie todos os diretórios e subdiretórios vazios (mesmo os que ainda não terão conteúdo agora).

2. Preencha os seguintes arquivos da RAIZ com conteúdo funcional e pronto para produção:

**Arquivos da raiz:**
- `.env.example` → Todas as variáveis necessárias (DB, Redis, ASAAS, JWT, Brevo, etc.) com valores de exemplo.
- `.gitignore` → Padrão completo para Python + Node + Docker.
- `README.md` → Documentação completa: descrição, como instalar, rodar em dev, testes, deploy, como customizar para B2B/B2C.
- `Makefile` → Comandos úteis: `make up`, `make down`, `make migrate`, `make test-backend`, `make frontend-dev`, `make seed`, etc.
- `docker-compose.yml` → Serviços completos: backend, frontend, postgres, redis, celery-worker, celery-beat. Use volumes corretos e dependa de postgres.
- `Dockerfile.backend` → Multi-stage build otimizado para FastAPI + Poetry.
- `Dockerfile.frontend` → Build multi-stage para Vite/React em produção.
- `.github/workflows/ci-backend.yml`, `ci-frontend.yml` e `deploy.yml` → Workflows funcionais (lint, test, build, deploy para Railway/Render).

3. Use as melhores práticas 2026: Poetry para Python, Node 20+, Docker best practices, healthchecks, etc.

4. Após criar tudo, execute `tree saas-boilerplate` e mostre a saída completa para confirmar a estrutura.

5. No final, informe: "Estrutura do Prompt 1 concluída – pronto para Prompt 2".

**NÃO adicione nenhum código dentro de `backend/app/` ou `frontend/src/` além dos arquivos da raiz. Apenas a estrutura e os arquivos raiz.**

**IMPORTANTE - Variáveis de Ambiente no .env.example:**
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/saas_db
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ASAAS (Billing) - NÃO USAR STRIPE
ASAAS_API_KEY=your-asaas-api-key
ASAAS_WEBHOOK_SECRET=your-webhook-secret
ASAAS_ENVIRONMENT=sandbox

# Brevo (Email) - NÃO USAR SENDGRID/RESEND
BREVO_API_KEY=your-brevo-api-key

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
ALLOWED_HOSTS=localhost,127.0.0.1

# Project
PROJECT_NAME=SaaS Boilerplate
API_V1_STR=/api/v1
DEBUG=true

# Monitoring
SENTRY_DSN=your-sentry-dsn
```
```

**Validação:**
```bash
cd saas-boilerplate
tree -L 3
docker compose config  # Valida docker-compose.yml
```

---

## 🎯 PROMPT 2 – Backend: Configuração Base e Dependências

**Tema:** Core do FastAPI + Config + Security + Tenant  
**Dependências:** Prompt 1 concluído  
**Tempo estimado:** 20-25 minutos

```markdown
Você é um engenheiro sênior de software especializado em FastAPI + SaaS multi-tenant.

**Contexto atual:**
- Projeto: saas-boilerplate
- Prompt 1 já executado (estrutura completa da raiz + Docker).
- Billing agora usa ASAAS (não Stripe).
- Email agora usa Brevo (não Resend/SendGrid).

**Tarefa:**
Crie e preencha os seguintes arquivos dentro de `backend/` e `backend/app/`:

1. `backend/pyproject.toml` → Dependências completas via Poetry com as seguintes bibliotecas principais:
   - fastapi, uvicorn[standard]
   - sqlmodel
   - alembic
   - pydantic-settings
   - python-jose[cryptography]
   - passlib[bcrypt]
   - httpx (para chamadas à API Asaas)
   - brevo-python (SDK oficial Brevo para emails transacionais)
   - redis
   - celery[redis]
   - structlog
   - python-multipart
   - pytest, pytest-asyncio, httpx (para testes)
   - Versões estáveis compatíveis com Python 3.12+ (use ^ ou * onde apropriado).

2. `backend/alembic.ini` → Configuração padrão do Alembic apontando para app.core.database.

3. `backend/app/main.py` → Aplicação FastAPI completa com:
   - title, version, docs_url, redoc_url
   - CORS middleware (origins do config)
   - Middleware de tenant
   - Startup e shutdown events (conexão Redis, etc.)
   - Inclusão de routers v1 (mesmo que ainda vazios)
   - Health check router

4. `backend/app/core/config.py` → Settings com Pydantic v2 (SettingsConfigDict):
   - Todas as variáveis de ambiente necessárias:
     - DATABASE_URL, REDIS_URL
     - JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
     - ASAAS_API_KEY, ASAAS_WEBHOOK_SECRET, ASAAS_ENVIRONMENT (sandbox ou production)
     - BREVO_API_KEY
     - CORS_ORIGINS, ALLOWED_HOSTS
     - PROJECT_NAME, API_V1_STR, etc.
   - Use model_config = ConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

5. `backend/app/core/database.py` → Engine assíncrono, SessionLocal, Base = SQLModel.metadata

6. `backend/app/core/security.py` → Funções completas:
   - create_access_token, create_refresh_token, decode_token
   - verify_password, get_password_hash
   - OAuth2PasswordBearer

7. `backend/app/core/tenant.py` → Middleware de multi-tenancy completo:
   - Extrai tenant_id do header "X-Tenant-ID" ou subdomínio
   - Injeta em request.state.tenant_id
   - Validação básica

8. `backend/app/core/cache.py` → Cliente Redis assíncrono + decorator simples @cached

**Requisitos obrigatórios:**
- Python 3.12+
- Pydantic v2 em todos os lugares (model_config)
- Nenhum import ou referência a Stripe em lugar nenhum
- Nenhum import ou referência a SendGrid/Resend
- Todos os arquivos devem ter imports corretos, __init__.py onde necessário
- Logging pronto com structlog (configure no main.py)
- Config deve carregar automaticamente do .env

**Após terminar todos os arquivos, execute:**
```bash
cd backend && poetry install --no-root
poetry run python -m pyright app
poetry run python -c "from app.core.config import settings; print('Config OK')"
```

Mostre a saída dos comandos acima.

No final, informe exatamente: "Prompt 2 concluído – Backend base (Brevo + ASAAS) pronto. Aguardando Prompt 3."
```

**Validação:**
```bash
cd backend
poetry install --no-root
poetry run python -c "from app.core.config import settings; print(settings.PROJECT_NAME)"
```

---

## 🎯 PROMPT 3 – Backend: Modelos e Schemas

**Tema:** SQLModel Models + Pydantic Schemas  
**Dependências:** Prompt 2 concluído  
**Tempo estimado:** 20-25 minutos

```markdown
Você é um engenheiro sênior de software especializado em FastAPI + SaaS multi-tenant.

**Contexto atual:**
- Projeto: saas-boilerplate
- Já foram criados: estrutura raiz, core completo (Prompt 1 e 2).
- Billing agora usa ASAAS (não Stripe).
- Email agora usa Brevo.

**Tarefa:**
Crie e preencha completamente as pastas `backend/app/models/` e `backend/app/schemas/`:

1. `backend/app/models/__init__.py`
2. `backend/app/models/base.py` → Classe Base com id (UUID), created_at, updated_at, is_deleted (soft-delete), tenant_id (UUID obrigatório).
3. `backend/app/models/user.py`
4. `backend/app/models/organization.py`
5. `backend/app/models/subscription.py` → Model Subscription adaptado para Asaas (campos: asaas_subscription_id, status, next_due_date, etc.)
6. `backend/app/models/audit_log.py`
7. `backend/app/schemas/__init__.py`
8. `backend/app/schemas/user.py` → Create, Read, Update, etc.
9. `backend/app/schemas/auth.py` → Token, LoginRequest, RegisterRequest, etc.
10. `backend/app/schemas/organization.py` → Create, Read, Invite
11. `backend/app/schemas/billing.py` → Schemas adaptados para ASAAS: Plan, SubscriptionRead, CheckoutRequest, WebhookEvent (eventos Asaas: PAYMENT_CONFIRMED, SUBSCRIPTION_CREATED, etc.), AsaasWebhookPayload
12. `backend/app/schemas/response.py` → Schemas genéricos de resposta

**Requisitos obrigatórios:**
- SQLModel (table=True) + Pydantic v2
- Todos os models com tenant_id
- Relationships corretas (User ↔ Organization, Subscription ↔ Organization)
- Schemas de billing totalmente renomeados/adaptados para Asaas (sem qualquer referência a Stripe)
- UUID para IDs
- Soft-delete em todos os models
- Timestamps (created_at, updated_at) em todos os models

**Após terminar, execute:**
```bash
cd backend
alembic revision --autogenerate -m "initial models"
```

Mostre a saída do comando.

No final, informe exatamente: "Prompt 3 concluído – Modelos e Schemas (ASAAS + Brevo) prontos. Aguardando Prompt 4."
```

**Validação:**
```bash
cd backend
poetry run python -c "from app.models import User, Organization; print('Models OK')"
```

---

## 🎯 PROMPT 4 – Backend: CRUD Genérico e Serviços

**Tema:** CRUD Layer + ASAAS Service + Brevo Service  
**Dependências:** Prompt 3 concluído  
**Tempo estimado:** 25-30 minutos

```markdown
Você é um engenheiro sênior de software especializado em FastAPI + SaaS multi-tenant.

**Contexto atual:**
- Projeto: saas-boilerplate
- Prompts 1, 2 e 3 já executados.
- Billing = ASAAS
- Email = Brevo

**Tarefa:**
Crie e preencha:

1. `backend/app/crud/__init__.py`
2. `backend/app/crud/base.py` → CRUD genérico (get, create, update, soft-delete, filter_by_tenant)
3. `backend/app/crud/user.py`
4. `backend/app/crud/organization.py`
5. `backend/app/crud/subscription.py`
6. `backend/app/services/__init__.py`
7. `backend/app/services/asaas_service.py` → Classe completa:
   - create_customer
   - create_subscription / create_checkout
   - create_payment_link
   - handle_webhook (suporte aos principais eventos Asaas: PAYMENT_CONFIRMED, PAYMENT_OVERDUE, SUBSCRIPTION_CREATED, SUBSCRIPTION_CANCELED, etc.)
   - sync_subscription
   - usar httpx para chamadas à API Asaas (base_url = https://api.asaas.com/v3)
8. `backend/app/services/email_service.py` → Funções assíncronas usando SDK Brevo (brevo_python):
   - send_welcome_email
   - send_password_reset
   - send_organization_invite
   - usar TransactionalEmailsApi
9. `backend/app/utils/pagination.py`

**Requisitos obrigatórios:**
- Todo CRUD respeita tenant_id automaticamente
- Asaas service usa settings.ASAAS_API_KEY e settings.ASAAS_WEBHOOK_SECRET
- Email service usa settings.BREVO_API_KEY
- Logging com structlog
- Webhook handler preparado para signature validation do Asaas
- Tudo com type hints e docstrings

**Após terminar, teste sintaxe com:**
```bash
cd backend
poetry run python -m pyright backend/app/services
```

No final, informe exatamente: "Prompt 4 concluído – CRUD e Serviços (ASAAS + Brevo) prontos. Aguardando Prompt 5."
```

**Validação:**
```bash
cd backend
poetry run python -c "from app.services.asaas_service import AsaasService; print('ASAAS Service OK')"
poetry run python -c "from app.services.email_service import EmailService; print('Brevo Service OK')"
```

---

## 🎯 PROMPT 5 – Backend: API Endpoints e Dependencies

**Tema:** REST API Complete + Auth Dependencies  
**Dependências:** Prompt 4 concluído  
**Tempo estimado:** 25-30 minutos

```markdown
Você é um engenheiro sênior de software especializado em FastAPI + SaaS multi-tenant.

**Contexto atual:**
- Projeto: saas-boilerplate
- Prompts 1–4 já executados (com ASAAS e Brevo).

**Tarefa:**
Crie toda a estrutura da API v1:

1. `backend/app/api/__init__.py`
2. `backend/app/api/v1/__init__.py`
3. `backend/app/api/v1/endpoints/__init__.py`
4. `backend/app/api/v1/endpoints/auth.py` → /login, /register, /refresh, /reset-password, /verify-email
5. `backend/app/api/v1/endpoints/users.py` → CRUD usuários (protegido)
6. `backend/app/api/v1/endpoints/organizations.py` → Create, list, update, invite
7. `backend/app/api/v1/endpoints/billing.py` → 
   - /plans (lista planos)
   - /checkout (cria assinatura Asaas)
   - /portal (gera link do portal Asaas)
   - /webhook (público – recebe eventos Asaas)
   - /subscription (status atual)
8. `backend/app/api/v1/endpoints/health.py`
9. `backend/app/api/v1/endpoints/core_feature.py` → Exemplo genérico
10. `backend/app/api/v1/dependencies/__init__.py`
11. `backend/app/api/v1/dependencies/current_user.py`
12. `backend/app/api/v1/dependencies/current_tenant.py`

**Requisitos obrigatórios:**
- Routers com prefix /api/v1
- Billing webhook é público (sem auth)
- Todos os outros endpoints usam Depends(current_user) + Depends(current_tenant)
- Schemas de response são os definidos no Prompt 3 (billing agora ASAAS)
- OpenAPI tags e summaries claros

**Após terminar, rode:**
```bash
cd backend
poetry run uvicorn app.main:app --reload
```

Teste com curl:
```bash
curl http://localhost:8000/api/v1/health
curl -X POST http://localhost:8000/api/v1/auth/login -H "Content-Type: application/json" -d '{"email":"test@example.com","password":"test123"}'
```

No final, informe exatamente: "Prompt 5 concluído – API Endpoints e Dependencies (ASAAS + Brevo) prontos. Backend completo. Aguardando Prompt 6."
```

**Validação:**
```bash
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/docs  # Verifica OpenAPI
```

---

## 🎯 PROMPT 6 – Backend: Background Tasks, Alembic e Testes

**Tema:** Celery Tasks + Migrations + Pytest  
**Dependências:** Prompt 5 concluído  
**Tempo estimado:** 25-30 minutos

```markdown
Você é um engenheiro sênior de software especializado em FastAPI + SaaS multi-tenant.

**Contexto atual:**
- Projeto: saas-boilerplate
- Prompts 1 a 5 já executados (core, models, schemas, crud, services com ASAAS e Brevo, endpoints completos).

**Tarefa:**

1. Configure o Alembic completamente:
   - `backend/alembic/env.py` → Configurado com SQLModel + target_metadata
   - `backend/alembic/script.py.mako`
   - Gere a primeira migration: `alembic revision --autogenerate -m "initial migration"`

2. `backend/app/background/tasks.py` → Tarefas assíncronas com Celery:
   - send_email_task (usa Brevo via email_service)
   - sync_asaas_subscription_task
   - process_audit_log_task

3. Crie a pasta `backend/tests/` com:
   - `backend/tests/conftest.py` → Fixtures (test client, test DB, superuser, tenant)
   - `backend/tests/test_auth.py`
   - `backend/tests/test_users.py`
   - `backend/tests/test_billing.py` (testes de ASAAS endpoints e webhook simulation)
   - `backend/tests/test_organizations.py`

**Requisitos obrigatórios:**
- Alembic deve usar o config do core/database
- Celery configurado no main.py com Redis broker
- Todos os testes usam pytest-asyncio e TestClient
- Testes de billing simulam webhooks Asaas (sem chamar API real)
- Coverage básico (>80% nos módulos testados)
- Use structlog nos testes

**Após terminar, execute:**
```bash
cd backend
poetry run alembic upgrade head
poetry run pytest -v --cov=app
```

Mostre a saída dos comandos.

No final, informe exatamente: "Prompt 6 concluído – Background Tasks, Alembic e Testes (ASAAS + Brevo) prontos. Backend 100% funcional. Aguardando Prompt 7."
```

**Validação:**
```bash
cd backend
poetry run pytest -v --cov=app --cov-report=term-missing
poetry run alembic current  # Verifica migrations aplicadas
```

---

## 🎯 PROMPT 7 – Frontend: Setup Completo e Configuração

**Tema:** React + Vite + TypeScript + shadcn/ui  
**Dependências:** Prompt 6 concluído  
**Tempo estimado:** 20-25 minutos

```markdown
Você é um engenheiro sênior de software especializado em React + TypeScript + SaaS.

**Contexto atual:**
- Projeto: saas-boilerplate
- Backend já completo (Prompts 1-6) com API em /api/v1 e endpoints ASAAS + Brevo.
- Stack frontend: React 19 + TypeScript + Vite + Tailwind + shadcn/ui + TanStack Query + Zustand.

**Tarefa:**
Crie e preencha toda a estrutura do frontend:

1. `frontend/package.json` → Dependências completas (React, @tanstack/react-query, zustand, react-hook-form, zod, axios, lucide-react, shadcn/ui, etc.)
2. `frontend/vite.config.ts` → Proxy para backend + plugins
3. `frontend/tsconfig.json`, `tailwind.config.ts`, `postcss.config.js`, `eslint.config.js`
4. `frontend/.env.example` → Variáveis (VITE_API_URL, etc.)
5. `frontend/public/favicon.ico` e `logo.svg` (pode usar placeholders)

**Estrutura src/:**
- `frontend/src/app/layout.tsx` → Root layout com providers (QueryClient, ThemeProvider, Toast)
- `frontend/src/app/page.tsx` → Landing page pública simples
- `frontend/src/lib/api.ts` → Axios client com interceptors (token + tenant_id header)
- `frontend/src/store/authStore.ts` e `tenantStore.ts` → Zustand stores
- `frontend/src/hooks/useAuth.tsx`, `useTenant.tsx`, `useApi.tsx`
- `frontend/src/types/index.ts` → Tipos globais (User, Organization, Subscription ASAAS)
- `frontend/src/constants/routes.ts`

**Requisitos obrigatórios:**
- shadcn/ui inicializado (button, input, card, etc.)
- Dark/light mode funcional
- API client envia automaticamente X-Tenant-ID e Authorization
- TypeScript strict mode
- Nenhum hard-coded de Stripe (use ASAAS nos tipos/comments)

**Após terminar, execute:**
```bash
cd frontend
npm install && npm run build
```

Mostre se deu sucesso.

No final, informe exatamente: "Prompt 7 concluído – Frontend setup completo. Aguardando Prompt 8."
```

**Validação:**
```bash
cd frontend
npm install
npm run build
npm run lint
```

---

## 🎯 PROMPT 8 – Frontend: Layout, Autenticação e Proteção de Rotas

**Tema:** UI Components + Auth Flow + Protected Routes  
**Dependências:** Prompt 7 concluído  
**Tempo estimado:** 25-30 minutos

```markdown
Você é um engenheiro sênior de software especializado em React + TypeScript + SaaS.

**Contexto atual:**
- Projeto: saas-boilerplate
- Prompt 7 já executado (setup frontend completo).
- Backend endpoints: /api/v1/auth/*, /organizations, /billing (ASAAS).

**Tarefa:**
Implemente o layout e fluxo de autenticação:

1. `frontend/src/components/layout/`:
   - `Header.tsx`
   - `Sidebar.tsx`
   - `TenantSwitch.tsx` (dropdown de organizações)

2. `frontend/src/components/ui/` → Componentes shadcn necessários (já inicializados no Prompt 7)

3. Páginas de autenticação:
   - `frontend/src/app/auth/login/page.tsx`
   - `frontend/src/app/auth/register/page.tsx`
   - `frontend/src/app/auth/reset-password/page.tsx` (opcional mas recomendado)

4. Páginas protegidas:
   - `frontend/src/app/dashboard/page.tsx`
   - `frontend/src/app/organizations/page.tsx`
   - `frontend/src/app/billing/page.tsx` (mostra planos, botão de checkout Asaas, portal)

5. Proteção de rotas:
   - Middleware de autenticação no layout.tsx
   - ProtectedRoute component ou useEffect com redirect

6. Fluxo completo:
   - Login → salva token + user no Zustand
   - Tenant selection
   - Dashboard com Sidebar
   - Integração com TanStack Query para fetching de user/org/subscription

**Requisitos obrigatórios:**
- React Hook Form + Zod em todos os forms
- Toast notifications (sonner ou similar)
- Loading states e error boundaries
- Chamadas à API usam o client do Prompt 7 (ex: billing/checkout chama /api/v1/billing/checkout)
- TenantSwitch atualiza header X-Tenant-ID automaticamente
- Design moderno, responsivo, dark mode

**Após terminar, execute:**
```bash
cd frontend
npm run dev
```

Confirme que as páginas de login e dashboard carregam (sem erros de build).

No final, informe exatamente: "Prompt 8 concluído – Layout, Autenticação e Proteção de Rotas prontos. Frontend funcional. Aguardando Prompt 9."
```

**Validação:**
```bash
cd frontend
npm run dev
# Acesse http://localhost:5173 e verifique login/dashboard
```

---

## 🎯 PROMPT 9 – Integração Frontend-Backend + Features SaaS

**Tema:** Full Integration + SaaS Features  
**Dependências:** Prompt 8 concluído  
**Tempo estimado:** 30-35 minutos

```markdown
Você é um engenheiro sênior de software especializado em React + FastAPI SaaS.

**Contexto atual:**
- Projeto: saas-boilerplate
- Backend 100% completo (Prompts 1-6) com ASAAS e Brevo.
- Frontend setup + layout + auth completo (Prompts 7-8).

**Tarefa:**
Conecte completamente o frontend com o backend e implemente as features SaaS:

1. Atualize `frontend/src/lib/api.ts` (se necessário) e hooks para usar todos os endpoints /api/v1

2. `frontend/src/app/dashboard/page.tsx` → Dashboard principal com overview (user, org, subscription status Asaas)

3. `frontend/src/app/organizations/page.tsx` → Lista, create, invite members + TenantSwitch funcional

4. `frontend/src/app/billing/page.tsx` → 
   - Lista de planos
   - Botão "Assinar" → chama /api/v1/billing/checkout (ASAAS)
   - Botão "Gerenciar Assinatura" → chama /api/v1/billing/portal
   - Status atual da assinatura (next_due_date, status)
   - Histórico de pagamentos

5. Fluxo de onboarding:
   - Após registro → redireciona para create organization
   - Welcome email (Brevo) disparado via backend
   - Toast de sucesso em todas as ações

6. Integração completa:
   - TanStack Query para todos os fetches (user, org, subscription, plans)
   - Zustand stores atualizados em tempo real
   - Error handling e loading states unificados

**Requisitos obrigatórios:**
- Todas as chamadas API usam o client com Authorization + X-Tenant-ID
- Billing pages usam schemas ASAAS do backend
- Design consistente com shadcn/ui + dark mode
- Onboarding checklist simples (3 passos)

**Após terminar, execute:**
```bash
cd frontend
npm run build
```

Confirme que não há erros de TypeScript ou build.

No final, informe exatamente: "Prompt 9 concluído – Integração Frontend-Backend + Features SaaS (ASAAS + Brevo) pronta. Aguardando Prompt 10."
```

**Validação:**
```bash
cd frontend
npm run build
npm run lint
# Teste fluxo completo: register → login → dashboard → billing
```

---

## 🎯 PROMPT 10 – CI/CD, Docker e Deploy

**Tema:** Production Infrastructure + GitHub Actions  
**Dependências:** Prompt 9 concluído  
**Tempo estimado:** 20-25 minutos

```markdown
Você é um engenheiro sênior de software especializado em DevOps + SaaS.

**Contexto atual:**
- Projeto: saas-boilerplate
- Todo o código (backend + frontend) já implementado e funcional.

**Tarefa:**
Finalize a infraestrutura de deploy:

1. Otimize os Dockerfiles (backend e frontend) já existentes com multi-stage e cache

2. Atualize `docker-compose.yml` com variáveis de ambiente corretas e healthchecks

3. Finalize os workflows GitHub Actions:
   - `.github/workflows/ci-backend.yml` (poetry install, lint, test, coverage)
   - `.github/workflows/ci-frontend.yml` (npm ci, build, test)
   - `.github/workflows/deploy.yml` (build + deploy para Railway/Render/Fly.io – use matrix para ambientes)

4. Crie `.github/workflows/docker-publish.yml` (opcional mas recomendado)

5. Adicione `render.yaml` ou `railway.json` na raiz (escolha uma plataforma como exemplo)

6. Atualize `Makefile` com comandos de deploy e production build

**Requisitos obrigatórios:**
- Zero-downtime deploy
- Secrets corretos no CI (usar GitHub Secrets)
- Environment separation (dev/staging/prod)
- Healthchecks em todos os serviços
- Frontend build otimizado e servido pelo backend em produção (ou separado)

**Após terminar, mostre a estrutura final dos workflows e execute:**
```bash
docker compose build
```

Para validar.

No final, informe exatamente: "Prompt 10 concluído – CI/CD, Docker e Deploy prontos. Aguardando Prompt 11."
```

**Validação:**
```bash
docker compose config
docker compose build
# Verifique .github/workflows/ para sintaxe YAML correta
```

---

## 🎯 PROMPT 11 – Testes E2E, Segurança e Observability

**Tema:** E2E Testing + Security Hardening + Monitoring  
**Dependências:** Prompt 10 concluído  
**Tempo estimado:** 25-30 minutos

```markdown
Você é um engenheiro sênior de software especializado em FastAPI + React SaaS.

**Contexto atual:**
- Projeto: saas-boilerplate
- Todo o código + CI/CD já implementado.

**Tarefa:**
Adicione a camada final de qualidade e segurança:

1. Testes E2E:
   - `frontend/playwright.config.ts`
   - `frontend/tests/e2e/auth.spec.ts`
   - `frontend/tests/e2e/dashboard.spec.ts`
   - `frontend/tests/e2e/billing.spec.ts`

2. Segurança:
   - Rate limiting no backend (slowapi ou middleware)
   - Audit log completo em todas as ações críticas (usando model AuditLog)
   - CSP, CORS e security headers no main.py
   - Validação OWASP Top 10 (já coberta em grande parte)

3. Observability:
   - Integração com Sentry (backend e frontend)
   - `backend/app/core/monitoring.py` + OpenTelemetry básico
   - Logging estruturado (structlog) em produção

4. Atualize `pyproject.toml` e `package.json` com dependências necessárias (slowapi, sentry-sdk, playwright, etc.)

**Requisitos obrigatórios:**
- Playwright roda com `npm run test:e2e`
- Rate limiting por tenant + IP
- Sentry pronto para erros críticos (inclua DSN no .env.example)
- Audit log automático via middleware ou dependency

**Após terminar, execute os testes E2E (headless) e mostre o relatório:**
```bash
cd frontend
npm run test:e2e
```

No final, informe exatamente: "Prompt 11 concluído – Testes E2E, Segurança e Observability prontos. Aguardando Prompt 12."
```

**Validação:**
```bash
cd frontend
npx playwright install
npm run test:e2e -- --headed  # Ou headless para CI
```

---

## 🎯 PROMPT 12 – Documentação, Seed e Finalização do Boilerplate

**Tema:** Final Documentation + Seed Script + Production Ready  
**Dependências:** Prompt 11 concluído  
**Tempo estimado:** 20-25 minutos

```markdown
Você é um engenheiro sênior de software especializado em boilerplates SaaS.

**Contexto atual:**
- Projeto: saas-boilerplate
- Todos os prompts anteriores (1 a 11) já executados.

**Tarefa – FINALIZAÇÃO:**

1. `infra/scripts/seed_db.py` → Script completo para criar superuser, organização padrão, planos ASAAS e dados iniciais

2. Atualize `docs/`:
   - `ARCHITECTURE.md`
   - `MULTI_TENANCY.md`
   - `ASAAS_INTEGRATION.md` (substitua qualquer menção antiga)
   - `BREVO_INTEGRATION.md`

3. `README.md` → Versão final completa (instalação, desenvolvimento, deploy, como remover multi-tenancy para B2C, roadmap)

4. Adicione feature flags simples (model + service básico)

5. Crie um comando único no Makefile: `make bootstrap` que roda tudo (migrate, seed, frontend build)

6. Adicione `.env.example` atualizado com todas as chaves ASAAS e BREVO

7. Verifique toda a árvore de diretórios e corrija qualquer import quebrado ou referência errada

**Requisitos obrigatórios:**
- README com badges (Docker, FastAPI, React, ASAAS, Brevo)
- Instruções claras para trocar ASAAS/Brevo por outro provedor
- Script seed deve funcionar com `poetry run python infra/scripts/seed_db.py`
- Projeto deve rodar 100% com `make up` + `make seed`

**Após terminar, execute:**
```bash
make bootstrap
```

(ou os comandos equivalentes) e mostre que o projeto inicia sem erros.

No final, informe exatamente: "Prompt 12 concluído – Boilerplate SaaS completo, documentado e pronto para produção. Projeto FINALIZADO!"
```

**Validação:**
```bash
make bootstrap
# Ou manualmente:
make up
make migrate
make seed
cd frontend && npm run build
```

---

## ✅ Checklist de Conclusão

### Após Todos os 12 Prompts

```markdown
□ Estrutura de diretórios completa
□ Backend FastAPI funcional com ASAAS + Brevo
□ Frontend React com autenticação + dashboard
□ Multi-tenancy implementado (tenant_id em todos os models)
□ Tests passing (>80% coverage)
□ CI/CD configurado (GitHub Actions)
□ Docker compose funcionando
□ Documentação completa (README + docs/)
□ Seed script funcional
□ Makefile com todos os comandos
□ .env.example completo
```

### Comandos Finais de Validação

```bash
# Raiz do projeto
cd saas-boilerplate

# Backend
cd backend
poetry install
poetry run pytest -v --cov=app
poetry run alembic upgrade head

# Frontend
cd ../frontend
npm install
npm run build
npm run test:e2e

# Docker
cd ..
docker compose up -d
docker compose ps

# Bootstrap completo
make bootstrap
```

---

## 📊 Progresso do Projeto

| Prompt | Tema | Status | Commit |
|--------|------|--------|--------|
| 1 | Estrutura + Raiz | ⬜ | `feat: init structure` |
| 2 | Backend Core | ⬜ | `feat: backend core` |
| 3 | Models + Schemas | ⬜ | `feat: db models` |
| 4 | CRUD + Services | ⬜ | `feat: crud services` |
| 5 | API Endpoints | ⬜ | `feat: api routes` |
| 6 | Tasks + Tests | ⬜ | `feat: tests tasks` |
| 7 | Frontend Setup | ⬜ | `feat: frontend init` |
| 8 | Layout + Auth | ⬜ | `feat: auth layout` |
| 9 | Integration | ⬜ | `feat: full integration` |
| 10 | CI/CD + Deploy | ⬜ | `feat: ci cd deploy` |
| 11 | E2E + Security | ⬜ | `feat: e2e security` |
| 12 | Docs + Finalize | ⬜ | `feat: final release` |

---

## 🔄 Como Lidar com Erros

### Se um Prompt Falhar

```markdown
1. Não avance para o próximo prompt
2. Peça para a IA corrigir os erros específicos
3. Execute os comandos de validação novamente
4. Só prossiga quando tudo estiver verde
```

### Se a IA "Esquecer" Regras

```markdown
Lembrete para colar no chat:
"LEMBRETE: Este projeto usa ASAAS (não Stripe) e Brevo (não SendGrid). 
Consulte RULES.md para restrições completas. 
Todos os models devem ter tenant_id e soft-delete."
```

### Se Houver Conflito de Imports

```bash
# Backend
cd backend
poetry run python -m pyright app

# Frontend
cd frontend
npm run lint
npm run build
```

---

## 📌 Dicas Finais

```markdown
1. Faça git commit após CADA prompt concluído
2. Mantenha os 3 arquivos (.md) na raiz para referência rápida
3. Use @RULES.md no chat da IDE para contexto global
4. Teste manualmente cada feature após implementação
5. Documente customizações específicas do seu produto
```

---

*Documento gerado para uso com IDEs assistidas por IA (Cursor, Windsurf, ClaudeCode, OpenCode, Antigravity, GitHub Copilot)*  
*Versão: 2026.1 | Stack: FastAPI + React | Billing: ASAAS | Email: Brevo*  
*Total de Prompts: 12 | Estimativa Total: 2.5-3.5 horas*