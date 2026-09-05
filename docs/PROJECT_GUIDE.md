# PROJECT_GUIDE.md - SaaS Boilerplate Agnóstico

## Visão Geral do Projeto

**Stack Principal:** FastAPI (Backend) + React (Frontend)  
**Versão do Guia:** 2026  
**Foco:** Boilerplate base reutilizável (multi-tenant por padrão, simplificado para B2C)

---

## 📋 Checklist Completo (Etapas 1-14)

### Etapa 1: Planejamento e Validação do Produto

```markdown
- [ ] Definir personas (B2B: empresa/equipe vs B2C: usuário individual)
- [ ] Validar problema + MVP (entrevistas ou landing page com waitlist)
- [ ] Escolher modelo de precificação (freemium, tiers, usage-based, annual discount)
- [ ] Mapear features core vs nice-to-have (priorizar com MoSCoW)
- [ ] Definir métricas de sucesso (MRR, churn, CAC, LTV, activation rate)
- [ ] Documentar requisitos não-funcionais (escalabilidade, GDPR/LGPD, uptime 99.9%)
```

### Etapa 2: Configuração Inicial do Boilerplate (Setup)

```markdown
- [ ] Estrutura de pastas limpa (backend/src + frontend/src)
- [ ] Docker + docker-compose (app, db, redis, celery)
- [ ] Git + .gitignore + pre-commit (black, isort, eslint, prettier)
- [ ] CI/CD básico (GitHub Actions: lint, test, build)
- [ ] Environment variables centralizadas (Pydantic Settings)
- [ ] FastAPI template oficial ou similar (com SQLModel/SQLAlchemy + Alembic)
- [ ] React + Vite + TypeScript + Tailwind + shadcn/ui (ou Chakra)
- [ ] CORS configurado + proxy local (frontend → backend)
```

### Etapa 3: Autenticação e Gerenciamento de Usuários

```markdown
- [ ] JWT (ou Clerk/Auth.js para B2B rápido)
- [ ] Login com email/password + social (Google, GitHub)
- [ ] Reset password + email verification
- [ ] Multi-tenancy (B2B): Organizations/Teams + convite por email
- [ ] RBAC simples (roles: owner, admin, member, viewer)
- [ ] Tenant isolation (tenant_id em todas as tabelas ou schema separado)
- [ ] Refresh token + logout em todos os dispositivos
- [ ] Rate limiting por IP e por tenant
```

### Etapa 4: Banco de Dados e Persistência

```markdown
- [ ] PostgreSQL (recomendado) ou MongoDB (se schema flexível)
- [ ] ORM: SQLModel (oficial) ou SQLAlchemy 2.0 + Pydantic v2
- [ ] Alembic para migrations
- [ ] Soft-delete + timestamps (created_at, updated_at)
- [ ] Indexes e constraints em tenant_id + chaves estrangeiras
- [ ] Backup automático + point-in-time recovery
- [ ] Row Level Security (RLS) no Postgres para isolamento extra
```

### Etapa 5: Desenvolvimento Backend (FastAPI)

```markdown
- [ ] Routers modulares (users, organizations, billing, core features)
- [ ] Pydantic schemas separados (input/output)
- [ ] Dependency injection (Depends) para current_user + current_tenant
- [ ] Background tasks (Celery + Redis ou FastAPI BackgroundTasks)
- [ ] WebSockets (se real-time necessário)
- [ ] OpenAPI docs automáticas + Redoc/Swagger customizado
- [ ] Versionamento de API (v1/ na URL)
- [ ] Health check + readiness/liveness endpoints
```

### Etapa 6: Desenvolvimento Frontend (React)

```markdown
- [ ] TanStack Query (React Query) para data fetching e cache
- [ ] React Router v6 + protected routes
- [ ] Zustand ou Context para estado global (user + tenant)
- [ ] Formulários com React Hook Form + Zod
- [ ] Componentes reutilizáveis (shadcn/ui ou similar)
- [ ] Dark/light mode + internacionalização (i18n)
- [ ] Loading states, error boundaries e toast notifications
- [ ] API client centralizado (axios ou fetch wrapper com token)
```

### Etapa 7: Integrações Essenciais para SaaS

```markdown
- [ ] Pagamentos: ASAAS (Checkout + Customer Portal + webhooks)
- [ ] Assinaturas, upgrades, downgrades, cancelamento + trial
- [ ] Emails transacionais: Brevo (templates + MJML)
- [ ] Armazenamento de arquivos: S3 (AWS) ou Cloudinary com tenant prefix
- [ ] Analytics: PostHog ou Mixpanel (event tracking)
- [ ] Notificações in-app (se necessário)
- [ ] Integração com ferramentas externas via webhooks (Zapier-ready)
```

### Etapa 8: Segurança e Compliance

```markdown
- [ ] HTTPS everywhere + HSTS
- [ ] Helmet equivalents (CORS, CSP, X-Frame-Options)
- [ ] OWASP Top 10 mitigado (SQL injection já coberto pelo ORM)
- [ ] Secrets management (Doppler ou AWS Secrets)
- [ ] GDPR/LGPD: consentimento, data export/delete
- [ ] Audit log de ações críticas (quem fez o quê)
- [ ] Rate limiting + brute force protection
- [ ] Secrets scanning no CI
```

### Etapa 9: Testes e Qualidade

```markdown
- [ ] Unit tests (pytest + pytest-asyncio no backend)
- [ ] Integration tests (FastAPI TestClient)
- [ ] E2E tests (Playwright ou Cypress no frontend)
- [ ] Coverage mínimo 80%
- [ ] Contract tests para API (Pact ou similar)
- [ ] Testes de segurança (OWASP ZAP ou Bandit)
- [ ] Lint + type checking (mypy + eslint)
```

### Etapa 10: Deploy e Infraestrutura

```markdown
- [ ] Docker + multi-stage builds
- [ ] CI/CD completo (test → build → deploy)
- [ ] Plataforma: Render, Railway, Fly.io ou AWS (ECS + RDS)
- [ ] Database: Neon ou Supabase (serverless Postgres) ou AWS RDS
- [ ] Reverse proxy (Caddy ou Traefik) + domínio customizado
- [ ] Environment separation (dev/staging/prod)
- [ ] Zero-downtime deploy (blue-green ou rolling)
```

### Etapa 11: Monitoramento e Observability

```markdown
- [ ] Logging estruturado (structlog ou Loguru)
- [ ] Metrics: Prometheus + Grafana (ou Sentry + OpenTelemetry)
- [ ] Error tracking: Sentry
- [ ] Performance: New Relic ou Datadog (opcional no início)
- [ ] Uptime monitoring (UptimeRobot ou Better Uptime)
- [ ] Alertas em Slack/Email para erros críticos
```

### Etapa 12: Analytics, Relatórios e Growth

```markdown
- [ ] Dashboard admin (Superuser ou custom com FastAPI + React)
- [ ] Relatórios de uso (MRR, churn, feature adoption)
- [ ] Feature flags (LaunchDarkly ou simples com DB)
- [ ] Onboarding flow (tour, checklist, welcome email)
- [ ] Referral program (opcional no boilerplate)
- [ ] SEO e landing page (Next.js se quiser SSR, mas React puro funciona)
```

### Etapa 13: Escalabilidade e Performance

```markdown
- [ ] Cache (Redis) em endpoints pesados
- [ ] Async everywhere (FastAPI é nativo)
- [ ] Horizontal scaling (Kubernetes se >10k usuários)
- [ ] Database sharding ou read replicas
- [ ] CDN para assets estáticos
- [ ] Query optimization + pagination em todas as listas
```

### Etapa 14: Operação, Manutenção e Pós-Lançamento

```markdown
- [ ] Plano de backup + disaster recovery
- [ ] Changelog e release notes automáticos
- [ ] Suporte (intercom ou email + help center)
- [ ] Atualizações de dependências mensais
- [ ] Revisão de segurança trimestral
- [ ] Métricas de saúde do produto (churn, NPS)
- [ ] Roadmap vivo (Notion ou Linear)
```

---

## 🌳 Estrutura de Diretórios Completa

```
saas-boilerplate/
├── .env.example                   ← Template de variáveis de ambiente
├── .gitignore
├── README.md                      ← Documentação completa do boilerplate
├── Makefile                       ← Comandos úteis (up, test, migrate, etc.)
├── docker-compose.yml             ← Orquestração completa (app, db, redis, etc.)
├── Dockerfile.backend
├── Dockerfile.frontend
├── .github/
│   └── workflows/
│       ├── ci-backend.yml
│       ├── ci-frontend.yml
│       └── deploy.yml
├── backend/
│   ├── pyproject.toml             ← Dependências (poetry)
│   ├── alembic.ini
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py               ← Entrada do FastAPI
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py         ← Configurações Pydantic v2
│   │   │   ├── security.py       ← JWT, hashing, OAuth2
│   │   │   ├── database.py       ← Engine + Session
│   │   │   ├── tenant.py         ← Middleware de multi-tenancy
│   │   │   └── cache.py          ← Redis client
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── endpoints/
│   │   │       │   ├── auth.py
│   │   │       │   ├── users.py
│   │   │       │   ├── organizations.py
│   │   │       │   ├── billing.py
│   │   │       │   ├── health.py
│   │   │       │   └── core_feature.py
│   │   │       └── dependencies/
│   │   │           ├── current_user.py
│   │   │           └── current_tenant.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py           ← Base com soft-delete e timestamps
│   │   │   ├── user.py
│   │   │   ├── organization.py
│   │   │   ├── subscription.py
│   │   │   └── audit_log.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── auth.py
│   │   │   ├── organization.py
│   │   │   ├── billing.py
│   │   │   └── response.py
│   │   ├── crud/
│   │   │   ├── __init__.py
│   │   │   ├── base.py           ← CRUD genérico
│   │   │   ├── user.py
│   │   │   ├── organization.py
│   │   │   └── subscription.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── asaas_service.py
│   │   │   ├── email_service.py
│   │   │   └── notification_service.py
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── pagination.py
│   │   │   └── validators.py
│   │   └── background/
│   │       └── tasks.py
│   ├── alembic/
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_auth.py
│       ├── test_users.py
│       └── test_billing.py
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── postcss.config.js
│   ├── eslint.config.js
│   ├── .env.example
│   ├── public/
│   │   ├── favicon.ico
│   │   └── logo.svg
│   └── src/
│       ├── app/
│       │   ├── layout.tsx
│       │   ├── page.tsx
│       │   ├── dashboard/
│       │   ├── auth/
│       │   ├── organizations/
│       │   └── billing/
│       ├── components/
│       │   ├── ui/
│       │   ├── layout/
│       │   ├── forms/
│       │   └── common/
│       ├── lib/
│       │   ├── api.ts
│       │   ├── auth.ts
│       │   └── utils.ts
│       ├── hooks/
│       ├── store/
│       ├── types/
│       ├── constants/
│       └── assets/
├── infra/
│   └── scripts/
│       └── seed_db.py
└── docs/
    ├── ARCHITECTURE.md
    ├── MULTI_TENANCY.md
    ├── ASAAS_INTEGRATION.md
    └── BREVO_INTEGRATION.md
```

---

## 🔧 Regras Globais do Projeto

### Stack Tecnológica

```yaml
Backend:
  - Python: 3.12+
  - Framework: FastAPI
  - ORM: SQLModel + SQLAlchemy 2.0
  - Database: PostgreSQL
  - Cache: Redis
  - Task Queue: Celery
  - Migrations: Alembic

Frontend:
  - React: 19+
  - Build Tool: Vite
  - Language: TypeScript (strict mode)
  - Styling: Tailwind CSS + shadcn/ui
  - State: Zustand
  - Data Fetching: TanStack Query
  - Forms: React Hook Form + Zod

Integrações:
  - Billing: ASAAS (NÃO usar Stripe)
  - Email: Brevo (NÃO usar SendGrid/Resend)
  - Auth: JWT + OAuth2
  - Monitoring: Sentry + OpenTelemetry
```

### Environment Variables Obrigatórias

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/saas_db
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ASAAS (Billing)
ASAAS_API_KEY=your-asaas-api-key
ASAAS_WEBHOOK_SECRET=your-webhook-secret
ASAAS_ENVIRONMENT=sandbox

# Brevo (Email)
BREVO_API_KEY=your-brevo-api-key

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
ALLOWED_HOSTS=localhost,127.0.0.1

# Project
PROJECT_NAME=SaaS Boilerplate
API_V1_STR=/api/v1
```

### Convenções de Código

```python
# Backend - Python/FastAPI
- Usar Pydantic v2 em todos os schemas (model_config = ConfigDict(...))
- Todos os models devem ter tenant_id (UUID)
- Soft-delete obrigatório em todos os models
- Timestamps: created_at, updated_at em todos os models
- Type hints obrigatórios em todas as funções
- Docstrings em todas as classes e funções públicas
- Logging com structlog
```

```typescript
// Frontend - React/TypeScript
- TypeScript strict mode ativado
- Componentes funcionais apenas (no classes)
- Hooks customizados para lógica reutilizável
- Zustand para estado global (auth + tenant)
- TanStack Query para server state
- shadcn/ui para componentes UI
- Dark/light mode suportado
```

---

## 📁 Descrição dos Arquivos Principais

### Raiz do Projeto

| Arquivo | Descrição |
|---------|-----------|
| `.env.example` | Template com todas as variáveis (DB, ASAAS, JWT, Redis, etc.) |
| `.gitignore` | Ignora node_modules, .env, __pycache__, etc. |
| `README.md` | Como instalar, rodar, testar, deploy e customizar |
| `Makefile` | Comandos: make up, make migrate, make test, make seed, etc. |
| `docker-compose.yml` | Serviços: backend, frontend, postgres, redis, celery-worker |
| `Dockerfile.backend` | Build multi-stage do FastAPI + Poetry |
| `Dockerfile.frontend` | Build do Vite/React para produção |

### Backend

| Arquivo | Descrição |
|---------|-----------|
| `pyproject.toml` | Dependências via Poetry (FastAPI, SQLModel, Alembic, Celery, etc.) |
| `alembic.ini` | Configuração do Alembic |
| `app/main.py` | Criação da aplicação FastAPI + routers e middlewares |
| `app/core/config.py` | Settings Pydantic (ambiente, CORS, JWT, ASAAS keys) |
| `app/core/security.py` | Funções de hash, JWT encode/decode, OAuth2 |
| `app/core/database.py` | Engine, SessionFactory e Base model |
| `app/core/tenant.py` | Middleware que injeta tenant_id em todas as requisições |
| `app/core/cache.py` | Cliente Redis + decorators de cache |
| `app/api/v1/endpoints/*.py` | Rotas da API (auth, users, organizations, billing, health) |
| `app/api/v1/dependencies/*.py` | Dependencies (current_user, current_tenant) |
| `app/models/*.py` | Modelos SQLModel (User, Organization, Subscription, AuditLog) |
| `app/schemas/*.py` | Pydantic schemas de request/response |
| `app/crud/*.py` | CRUD genérico e implementações específicas |
| `app/services/asaas_service.py` | Integração completa com ASAAS |
| `app/services/email_service.py` | Envio de emails transacionais (Brevo) |
| `app/background/tasks.py` | Tarefas assíncronas (Celery) |
| `tests/*.py` | Testes unitários e de integração |

### Frontend

| Arquivo | Descrição |
|---------|-----------|
| `package.json` | Scripts e dependências (React, TanStack Query, Zustand, shadcn/ui) |
| `vite.config.ts` | Configuração Vite + proxy para backend |
| `tsconfig.json` | Configuração TypeScript |
| `tailwind.config.ts` | Tema Tailwind + shadcn |
| `src/app/layout.tsx` | Layout raiz com providers (QueryClient, Theme) |
| `src/app/page.tsx` | Landing page pública |
| `src/app/dashboard/page.tsx` | Dashboard principal protegido |
| `src/app/auth/*/page.tsx` | Páginas de login e cadastro |
| `src/components/ui/*` | Componentes shadcn reutilizáveis |
| `src/components/layout/*` | Sidebar, Header, TenantSwitch |
| `src/lib/api.ts` | Cliente HTTP com token automático e interceptors |
| `src/hooks/*.tsx` | Hooks customizados (useAuth, useTenant) |
| `src/store/*.ts` | Zustand stores globais (authStore, tenantStore) |
| `src/types/index.ts` | Tipos TypeScript compartilhados |

### Pastas Auxiliares

| Arquivo | Descrição |
|---------|-----------|
| `infra/scripts/seed_db.py` | Script para popular banco com dados iniciais |
| `docs/ARCHITECTURE.md` | Diagrama e explicação da arquitetura |
| `docs/MULTI_TENANCY.md` | Como funciona e como customizar o multi-tenancy |
| `docs/ASAAS_INTEGRATION.md` | Como configurar e testar webhooks ASAAS |
| `docs/BREVO_INTEGRATION.md` | Como configurar emails transacionais Brevo |

---

## ⚠️ Restrições Importantes

```markdown
CRITICAL - NUNCA USE:
❌ Stripe (usar ASAAS para billing)
❌ SendGrid ou Resend (usar Brevo para emails)
❌ MongoDB (usar PostgreSQL)
❌ Classes no React (usar functional components)
❌ Any sem type hint no Python
❌ Hardcoded secrets no código

OBRIGATÓRIO:
✅ tenant_id em todos os models do backend
✅ Soft-delete em todos os models
✅ Pydantic v2 com model_config
✅ TypeScript strict mode no frontend
✅ Environment variables via .env
✅ Docker para desenvolvimento e produção
✅ CI/CD com GitHub Actions
✅ Testes com coverage mínimo 80%
```

---

## 🚀 Comandos Makefile Principais

```bash
# Desenvolvimento
make up              # Sobe todos os serviços (docker-compose)
make down            # Derruba todos os serviços
make frontend-dev    # Roda frontend em dev mode
make backend-dev     # Roda backend em dev mode

# Database
make migrate         # Roda migrations do Alembic
make seed            # Popula banco com dados iniciais

# Testes
make test-backend    # Roda testes do backend
make test-frontend   # Roda testes do frontend
make test-e2e        # Roda testes E2E

# Build & Deploy
make build           # Build de produção
make deploy          # Deploy para produção
make bootstrap       # Roda tudo (migrate + seed + build)
```

---

## 📌 Dicas Finais para o Boilerplate

```markdown
1. Comece com o Full Stack FastAPI Template oficial (tiangolo) e adicione ASAAS + multi-tenancy
2. Para B2B: priorize Organizations + RBAC desde o dia 1
3. Para B2C: simplifique removendo tenant layer
4. Tempo estimado para boilerplate completo: 1-2 semanas (seguindo este checklist)
5. Repositórios de referência: FastAPI official full-stack, FastSaaS, TechWithTim B2B example
```

---

## 🔗 Próximos Passos

1. **IMPLEMENTATION_PLAN.md** - Contém os 12 prompts sequenciais para execução
2. **.cursorrules** - Contém as regras globais para a IDE
3. Execute os prompts em ordem (Prompt 1 → Prompt 12)
4. Faça git commit após cada prompt concluído

---

*Documento gerado para uso com IDEs assistedas por IA (Cursor, Windsurf, Antigravity, Opencode)*  
*Versão: 2026 | Stack: FastAPI + React | Billing: ASAAS | Email: Brevo*