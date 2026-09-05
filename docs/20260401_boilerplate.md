# SaaS Boilerplate - Documentação Técnica Completa

**Gerado:** 2026-04-01  
**Versão:** 0.1.0  
**Status:** Desenvolvimento/Pré-Produção

---

## 1. Visão Geral do Projeto

Projeto multi-tenant SaaS com FastAPI (backend) e React/TypeScript (frontend). Inclui autenticação, billing (Asaas), emails (Brevo) e tarefas em background (Celery).

**Stack Tecnológico:**
- **Backend:** FastAPI 0.116+, Python 3.12+, SQLModel, AsyncPG
- **Frontend:** React 19, TypeScript, Vite, TailwindCSS
- **Database:** PostgreSQL 16 (async)
- **Cache/Queue:** Redis 7
- **Task Queue:** Celery
- **Auth:** JWT com refresh tokens
- **Payments:** Asaas (gateway brasileiro)
- **Email:** Brevo

---

## 2. Árvore de Diretórios

```
boilerplate_v01/
├── .env                          # Variáveis de ambiente
├── .env.example                  # Template de variáveis
├── .gitignore
├── README.md
├── Makefile                      # Comandos de desenvolvimento
├── docker-compose.yml           # Compose produção
├── docker-compose.dev.yml       # Compose desenvolvimento
├── Dockerfile.backend
├── Dockerfile.frontend
├── Dockerfile.frontend-dev
├── render.yaml                   # Deploy Render.com

├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # Entry point FastAPI
│   │   │
│   │   ├── api/v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py         # /auth/*
│   │   │   │   ├── users.py        # /users/*
│   │   │   │   ├── organizations.py # /organizations/*
│   │   │   │   ├── billing.py       # /billing/*
│   │   │   │   ├── health.py        # /health
│   │   │   │   └── core_feature.py  # /core-feature
│   │   │   └── dependencies/
│   │   │       ├── current_user.py
│   │   │       └── current_tenant.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py          # Settings Pydantic
│   │   │   ├── database.py        # SQLModel async
│   │   │   , security.py          # JWT/password
│   │   │   ├── tenant.py          # Middleware tenant
│   │   │   ├── cache.py           # Redis (stub)
│   │   │   , limiter.py           # Rate limiting
│   │   │   └── security_headers.py
│   │   │
│   │   ├── models/
│   │   │   ├── base.py           # BaseModel
│   │   │   ├── user.py
│   │   │   ├── organization.py
│   │   │   , subscription.py
│   │   │   , asaas_customer.py
│   │   │   , asaas_webhook_event.py
│   │   │   , audit_log.py
│   │   │   , email_delivery.py
│   │   │   └── feature_flag.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── auth.py
│   │   │   , user.py
│   │   │   , organization.py
│   │   │   , billing.py
│   │   │   └── response.py
│   │   │
│   │   ├── services/
│   │   │   ├── asaas_service.py
│   │   │   , email_service.py
│   │   │   , audit_service.py
│   │   │   └── feature_flag_service.py
│   │   │
│   │   ├── crud/
│   │   │   ├── base.py
│   │   │   , user.py
│   │   │   , organization.py
│   │   │   └── subscription.py
│   │   │
│   │   └── background/
│   │       └── tasks.py          # Celery tasks
│   │
│   ├── tests/                    # pytest
│   ├── alembic/                  # Migrations
│   └── pyproject.toml            # Poetry

├── frontend/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── types/index.ts
│   │   ├── lib/api.ts
│   │   ├── hooks/
│   │   │   ├── useAuth.tsx
│   │   │   ├── useTenant.tsx
│   │   │   └── useApi.tsx
│   │   └── store/
│   │       ├── authStore.ts
│   │       └── tenantStore.ts
│   ├── tests/e2e/                # Playwright
│   └── package.json

├── docs/
│   ├── ARCHITECTURE.md
│   ├── MULTI_TENANCY.md
│   ├── ASAAS_INTEGRATION.md
│   ├── BREVO_INTEGRATION.md
│   ├── OPERATIONS.md
│   └── PROJECT_GUIDE.md

└── .github/workflows/
    ├── ci-backend.yml
    ├── ci-frontend.yml
    └── deploy.yml
```

---

## 3. Endpoints da API

### 3.1 Auth (`/api/v1/auth`)

| Método | Endpoint | Rate Limit | Auth | Descrição |
|--------|----------|------------|------|-----------|
| POST | /login | 10/min | Não | Login usuário |
| POST | /register | 5/min | Não | Registro novo |
| POST | /refresh | 20/min | Não | Refresh token |
| POST | /reset-password | 5/min | Não | Solicita reset |
| POST | /reset-password/confirm | - | Não | Confirma reset |
| POST | /verify-email | - | Não | Verifica email |
| POST | /logout-all | - | Sim | Revoga sessões |

**Contratos:**

```python
# POST /login
{email: EmailStr, password: str(min=8)}
→ {access_token, refresh_token, token_type}

# POST /register
{email, password, full_name?, organization_name?}
→ Token

# POST /refresh
{refresh_token: str}
→ Token

# POST /reset-password
{email: EmailStr}
→ {message: str}

# POST /reset-password/confirm
{token: str, new_password: str(min=8)}
→ {message: str}
```

### 3.2 Users (`/api/v1/users`)

| Método | Endpoint | Auth | Descrição |
|--------|----------|------|-----------|
| GET | / | Sim | Lista usuários (tenant) |
| GET | /me | Sim | Usuário atual |

### 3.3 Organizations (`/api/v1/organizations`)

| Método | Endpoint | Auth | Role | Descrição |
|--------|----------|------|------|-----------|
| GET | / | Sim | qualquer | Lista organizações |
| POST | / | Sim | owner/admin | Cria organização |

### 3.4 Billing (`/api/v1/billing`)

| Método | Endpoint | Auth | Descrição |
|--------|----------|------|-----------|
| GET | /plans | Não | Planos disponíveis |
| POST | /checkout | Sim | Cria assinatura |
| POST | /portal | Sim | URL portal cliente |
| POST | /webhook | Não | Webhook Asaas |
| GET | /subscription | Sim | Assinatura atual |

**Planos:**

```python
{
  "starter": {"id": "starter", "name": "Starter", "amount": 49.0, "billing_cycle": "MONTHLY"},
  "growth": {"id": "growth", "name": "Growth", "amount": 149.0, "billing_cycle": "MONTHLY"},
  "scale": {"id": "scale", "name": "Scale", "amount": 399.0, "billing_cycle": "MONTHLY"}
}
```

### 3.5 Health (`/api/v1/health`)

| Método | Endpoint | Auth | Descrição |
|--------|----------|------|-----------|
| GET | / | Não | Health check |

---

## 4. Banco de Dados

### 4.1 BaseModel (todas as tabelas)

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | UUID | PK |
| tenant_id | UUID | **Isolamento multi-tenant** |
| is_deleted | bool | Soft delete |
| created_at | datetime | Criação (UTC) |
| updated_at | datetime | Atualização (UTC) |

### 4.2 Tabelas

**organization:**
- id (UUID, PK), tenant_id (UUID), name (str), is_deleted, created_at, updated_at

**user:**
- id, tenant_id, organization_id (FK), email (unique), full_name, hashed_password, role (member/admin/owner), is_active, email_verified, reset_password_token, reset_password_expires_at, email_verification_token, refresh_token_version, last_login_at, is_deleted, created_at, updated_at

**subscription:**
- id, tenant_id, organization_id (FK), asaas_customer_id, asaas_subscription_id, plan_id, status (PENDING/ACTIVE/CANCELED), value, billing_cycle, next_due_date, activated_at, canceled_at, last_synced_at, is_deleted, created_at, updated_at

**asaas_customer:**
- id, tenant_id, organization_id (FK), asaas_customer_id (unique), name, email, cpf_cnpj, is_deleted, created_at, updated_at

**asaas_webhook_event:**
- id, tenant_id, organization_id (FK), event, external_id, payload (JSON), processed_at, processing_status (pending/processed/failed), failure_reason, received_at, is_deleted, created_at, updated_at

**audit_log:**
- id, tenant_id, actor_user_id, action, entity_type, entity_id, details, is_deleted, created_at, updated_at

**email_delivery:**
- id, tenant_id, template_key, recipient_email, payload (JSON), idempotency_key (unique), provider_message_id, status (queued/sent/failed), attempts, last_error, sent_at, is_deleted, created_at, updated_at

**feature_flag:**
- id, tenant_id, key (unique), enabled, is_deleted, created_at, updated_at

---

## 5. Fluxos End-to-End

### 5.1 Registro
```
1. POST /auth/register (email, password, full_name, organization_name)
2. Backend cria: Organization, User (role=owner), AuditLog
3. Celery: send_welcome_email
4. Retorna: Token (access + refresh)
```

### 5.2 Login
```
1. POST /auth/login (rate limit 10/min)
2. Valida credenciais + brute-force protection (5 falhas = 15min block)
3. Cria JWT com tenant_id + rtv (refresh_token_version)
4. AuditLog: auth.login
5. Retorna: Token
```

### 5.3 Checkout
```
1. POST /billing/checkout (plan_id)
2. AsaasService.ensure_customer() → cria customer Asaas
3. AsaasService.create_checkout() → cria subscription Asaas
4. Salva/Atualiza Subscription local
5. AuditLog: billing.checkout
6. Retorna: {subscription_id, status}
```

### 5.4 Webhook
```
1. POST /billing/webhook (access_token validation)
2. Salva AsaasWebhookEvent (pending)
3. AsaasService.sync_subscription_from_webhook() → atualiza status
4. Atualiza webhook event (processed/failed)
5. AuditLog: billing.webhook_processed
```

### 5.5 Multi-Tenant
```
1. Request inclui header X-Tenant-ID
2. TenantMiddleware extrai e valida UUID
3. get_current_tenant verifica tenant = current_user.tenant_id
4. Queries incluem: tenant_id + is_deleted=false
```

---

## 6. Segurança

- **JWT:** HS256, access=30min, refresh=7 dias
- **Password:** bcrypt via passlib
- **Rate Limiting:** slowapi (global 200/min, específicos)
- **Brute-force:** Dict em memória (5 falhas/15min)
- **Security Headers:** CSP, X-Frame-Options, nosniff
- **CORS:** allow_origins, allow_credentials=true, allow_headers=Authorization,Content-Type,X-Tenant-ID

---

## 7. Integrações

### Asaas (Payments)
- Sandbox: https://sandbox.asaas.com/api/v3
- Production: https://api.asaas.com/api/v3
- Endpoints: /customers, /subscriptions, /customers/{id}/portalUrl

### Brevo (Email)
- Base: https://api.brevo.com/v3
- Endpoint: POST /smtp/email
- Templates: welcome, reset_password, invite

### Celery
- Broker: Redis
- Task: send_transactional_email_task (welcome, reset, invite)

---

## 8. Variáveis de Ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| DATABASE_URL | postgresql+asyncpg://... | PostgreSQL |
| REDIS_URL | redis://... | Redis |
| REDIS_PASSWORD | dev-redis-password-123456 | Redis auth |
| JWT_SECRET_KEY | jwt-secret-key-123456 | **Mudar produção** |
| JWT_ALGORITHM | HS256 | |
| ACCESS_TOKEN_EXPIRE_MINUTES | 30 | |
| REFRESH_TOKEN_EXPIRE_DAYS | 7 | |
| ASAAS_API_KEY | aact_hmlg_... | Asaas |
| ASAAS_WEBHOOK_SECRET | whsec_... | Webhook validation |
| ASAAS_ENVIRONMENT | sandbox | sandbox/production |
| BREVO_API_KEY | xkeysib-... | Brevo |
| BREVO_SENDER_EMAIL | admin@solunna.com.br | |
| BREVO_SENDER_NAME | Solunna | |
| CORS_ORIGINS | http://localhost:3000,http://localhost:5173 | |
| PROJECT_NAME | SaaS Boilerplate | |

---

## 9. Scripts de Desenvolvimento

```bash
make up          # docker compose up -d --build
make down        # docker compose down
make migrate     # alembic upgrade head
make seed        # python infra/scripts/seed_db.py
make test-backend  # pytest -v --cov=app
make bootstrap   # migrate + seed + build
```

---

## 10. Maturity Assessment

| Funcionalidade | Status |
|----------------|--------|
| Registro/Login | ✅ Completo |
| Password Reset | ✅ Completo |
| Multi-tenant | ✅ Completo |
| Billing Asaas | ✅ Completo |
| Webhooks | ✅ Completo |
| Email Brevo | ✅ Completo |
| Audit Logs | ⚠️ Parcial |
| Rate Limiting | ⚠️ Parcial |
| User/Org CRUD | ⚠️ Parcial |

| Segurança | Nível |
|-----------|-------|
| Auth JWT | Bom |
| Password bcrypt | Bom |
| Tenant Isolation | Bom |
| Rate Limit | Parcial |
| Token Revocation | Fraco |

| Qualidade | Status |
|-----------|--------|
| Type Hints | Bom |
| Linting | ✅ Configurado |
| Tests | ⚠️ Básicos |
| CI/CD | ✅ GitHub Actions |

---

## 11. Problemas Conhecidos

**Críticos:**
1. JWT secret com valor padrão
2. FAILED_LOGINS em memória (não distribuído)
3. Cache decorator não implementado

**Altos:**
1. Tenant middleware aceita header ausente silenciosamente
2. Rate limits em endpoints sensíveis ausentes
3. Rate limiter não processa X-Forwarded-For

**Médios:**
1. Token revocation não invalida sessões ativas
2. Email verification não enforced no login
3. Audit logs ausentes em password reset confirm

---

*Documento gerado em 2026-04-01 para compreensão da estrutura e maturidade do projeto por LLMs.*