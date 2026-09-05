# RULES.md - AI Agent Project Rules (IDE Agnostic)

**Versão:** 2026 | **Projeto:** saas-boilerplate | **Stack:** FastAPI + React

---

## 🎯 Objetivo deste Arquivo

Este arquivo contém **todas as regras globais** que todo agente de IA deve seguir ao trabalhar neste projeto. Leia este arquivo **antes de qualquer tarefa** e mantenha essas regras em contexto durante toda a sessão.

---

## 📦 Stack Tecnológica Obrigatória

### Backend (Python/FastAPI)

```yaml
Linguagem: Python 3.12+
Framework: FastAPI
ORM: SQLModel + SQLAlchemy 2.0
Database: PostgreSQL (asyncpg)
Cache: Redis
Task Queue: Celery
Migrations: Alembic
Auth: JWT + OAuth2
Logging: structlog
Package Manager: Poetry
```

### Frontend (React/TypeScript)

```yaml
Framework: React 19+
Build Tool: Vite
Language: TypeScript (strict mode)
Styling: Tailwind CSS + shadcn/ui
State Management: Zustand
Data Fetching: TanStack Query
Forms: React Hook Form + Zod
Package Manager: npm ou pnpm
```

### Integrações Externas (CRÍTICO)

```yaml
Billing: ASAAS (NUNCA use Stripe)
Email: Brevo (NUNCA use SendGrid, Resend ou SES)
Auth Provider: JWT próprio (ou Clerk se acelerar B2B)
Monitoring: Sentry + OpenTelemetry
File Storage: AWS S3 ou Cloudinary
```

---

## ⚠️ Restrições Absolutas (NUNCA QUEBRE)

### Proibições de Tecnologia

```markdown
❌ NUNCA use Stripe para billing → Use ASAAS
❌ NUNCA use SendGrid/Resend para email → Use Brevo
❌ NUNCA use MongoDB → Use PostgreSQL
❌ NUNCA use classes no React → Use functional components + hooks
❌ NUNCA use `Any` sem type hint no Python
❌ NUNCA hardcode secrets no código → Use .env sempre
❌ NUNCA use SQLAlchemy 1.x → Use SQLAlchemy 2.0+
❌ NUNCA use Pydantic v1 → Use Pydantic v2 com model_config
```

### Requisitos Obrigatórios

```markdown
✅ tenant_id (UUID) em TODOS os models do backend
✅ Soft-delete (is_deleted) em TODOS os models
✅ Timestamps (created_at, updated_at) em TODOS os models
✅ TypeScript strict mode ativado no frontend
✅ Environment variables via .env (nunca hardcoded)
✅ Docker para desenvolvimento e produção
✅ CI/CD com GitHub Actions
✅ Testes com coverage mínimo 80%
✅ Type hints em TODAS as funções Python
✅ Docstrings em classes e funções públicas
```

---

## 📁 Estrutura de Diretórios (Resumo)

```
saas-boilerplate/
├── backend/
│   ├── app/
│   │   ├── core/          # Config, security, database, tenant, cache
│   │   ├── api/v1/        # Endpoints + dependencies
│   │   ├── models/        # SQLModel models (todos com tenant_id)
│   │   ├── schemas/       # Pydantic v2 schemas
│   │   ├── crud/          # CRUD genérico + específico
│   │   ├── services/      # ASAAS, Brevo, notifications
│   │   ├── utils/         # Pagination, validators
│   │   └── background/    # Celery tasks
│   ├── alembic/           # Migrations
│   └── tests/             # Pytest tests
├── frontend/
│   ├── src/
│   │   ├── app/           # Pages (Next.js-like structure)
│   │   ├── components/    # UI + layout + forms
│   │   ├── lib/           # API client, auth utils
│   │   ├── hooks/         # Custom hooks
│   │   ├── store/         # Zustand stores
│   │   └── types/         # TypeScript types
│   └── public/
├── .github/workflows/     # CI/CD
├── infra/scripts/         # Seed e scripts auxiliares
└── docs/                  # Documentação técnica
```

---

## 🔑 Environment Variables Obrigatórias

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/saas_db
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-secret-key-min-32-chars
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
DEBUG=true

# Monitoring
SENTRY_DSN=your-sentry-dsn
```

### Frontend (.env)

```bash
VITE_API_URL=http://localhost:8000
VITE_SENTRY_DSN=your-sentry-dsn
VITE_APP_NAME=SaaS Boilerplate
```

---

## 🏗️ Padrões de Código

### Backend (Python)

```python
# ✅ CORRETO - Pydantic v2
from pydantic import BaseModel, ConfigDict

class UserCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    
    email: str
    password: str
    tenant_id: UUID

# ✅ CORRETO - SQLModel com tenant_id
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime

class UserBase(SQLModel):
    tenant_id: UUID = Field(foreign_key="organization.id")
    email: str = Field(index=True, unique=True)
    is_deleted: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# ✅ CORRETO - Dependency injection
from fastapi import Depends

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_session)
) -> User:
    ...

# ❌ ERRADO - Pydantic v1 style
class UserCreate(BaseModel):
    class Config:
        anystr_strip_whitespace = True
```

### Frontend (TypeScript/React)

```typescript
// ✅ CORRETO - Functional component + hooks
import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'

export function DashboardPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['user'],
    queryFn: () => api.get('/api/v1/users/me')
  })

  if (isLoading) return <LoadingSpinner />
  return <div>{data.email}</div>
}

// ✅ CORRETO - TypeScript strict types
interface User {
  id: string
  email: string
  tenantId: string
  createdAt: string
}

// ❌ ERRADO - Classes ou Any sem tipo
class Dashboard extends React.Component {} // Não use
const data: any = {} // Não use
```

---

## 🔐 Segurança e Multi-Tenancy

### Regras de Tenant Isolation

```markdown
1. TODA query ao banco DEVE filtrar por tenant_id
2. TODA requisição DEVE passar por current_tenant dependency
3. Webhooks de billing são ÚNICOS endpoints públicos (sem auth)
4. Audit log em TODAS as ações críticas (create, update, delete)
5. Rate limiting por IP + por tenant_id
```

### Implementação do Middleware de Tenant

```python
# backend/app/core/tenant.py
from fastapi import Request, HTTPException

async def tenant_middleware(request: Request, call_next):
    tenant_id = request.headers.get("X-Tenant-ID")
    if not tenant_id and not is_public_endpoint(request.url.path):
        raise HTTPException(status_code=400, detail="X-Tenant-ID required")
    request.state.tenant_id = tenant_id
    return await call_next(request)
```

---

## 🧪 Testes e Qualidade

### Backend Tests

```bash
# Comando para rodar testes
cd backend && poetry run pytest -v --cov=app --cov-report=term-missing

# Coverage mínimo obrigatório: 80%
# Testes obrigatórios: auth, users, organizations, billing
```

### Frontend Tests

```bash
# Unit tests
cd frontend && npm run test

# E2E tests
cd frontend && npm run test:e2e
```

### CI/CD Checks

```yaml
# GitHub Actions deve validar:
- Lint (black, isort, eslint, prettier)
- Type check (mypy, tsc --noEmit)
- Tests (pytest, jest/playwright)
- Build (docker build, npm build)
- Security (bandit, npm audit)
```

---

## 📝 Convenções de Nomenclatura

### Backend

```python
# Arquivos: snake_case
# Classes: PascalCase
# Funções: snake_case
# Variáveis: snake_case
# Constants: UPPER_SNAKE_CASE

# Exemplo
app/core/config.py
app/models/user.py
class UserCreate(BaseModel)
def get_current_user()
DATABASE_URL
```

### Frontend

```typescript
// Arquivos: PascalCase para components, kebab-case para páginas
// Components: PascalCase
// Funções/Hooks: camelCase
// Types/Interfaces: PascalCase
// Constants: UPPER_SNAKE_CASE

// Exemplo
src/components/layout/Sidebar.tsx
src/app/dashboard/page.tsx
function useAuth()
interface UserResponse
API_V1_URL
```

---

## 🚀 Comandos Makefile Principais

```bash
# Desenvolvimento
make up              # Sobe todos os serviços Docker
make down            # Derruba todos os serviços
make backend-dev     # Roda backend em dev mode
make frontend-dev    # Roda frontend em dev mode

# Database
make migrate         # Roda migrations Alembic
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

## 📚 Documentação de Referência

| Arquivo | Descrição |
|---------|-----------|
| `PROJECT_GUIDE.md` | Checklist completo das 14 etapas do SaaS |
| `IMPLEMENTATION_PLAN.md` | 12 prompts sequenciais para execução com IA |
| `docs/ARCHITECTURE.md` | Diagrama e explicação da arquitetura |
| `docs/MULTI_TENANCY.md` | Como funciona o isolamento de tenants |
| `docs/ASAAS_INTEGRATION.md` | Configuração e webhooks ASAAS |
| `docs/BREVO_INTEGRATION.md` | Configuração de emails Brevo |

---

## 🔄 Fluxo de Trabalho com IA

### Antes de Cada Tarefa

```markdown
1. Leia este arquivo RULES.md completamente
2. Leia PROJECT_GUIDE.md para contexto da etapa atual
3. Verifique IMPLEMENTATION_PLAN.md para o prompt correto
4. Confirme que está seguindo as restrições de stack (ASAAS, Brevo, etc.)
```

### Após Cada Tarefa

```markdown
1. Execute type check (mypy + tsc --noEmit)
2. Execute testes relacionados
3. Faça git commit com mensagem descritiva
4. Atualize documentação se necessário
5. Valide com `make bootstrap` se for mudança estrutural
```

### Validação de Código Gerado

```markdown
Antes de considerar uma tarefa concluída, verifique:
□ Imports estão corretos e sem erros
□ Type hints estão presentes em todas as funções
□ tenant_id está em todos os models/queries
□ Não há referências a Stripe/SendGrid
□ Environment variables estão no .env.example
□ Tests foram adicionados/atualizados
□ Documentation foi atualizada se necessário
```

---

## 🎯 Prompt de Contexto para IA

Quando iniciar uma nova sessão com qualquer agente de IA, use este prompt:

```
Você está trabalhando no projeto saas-boilerplate (FastAPI + React SaaS).

REGRAS CRÍTICAS:
1. Billing: ASAAS (nunca Stripe)
2. Email: Brevo (nunca SendGrid/Resend)
3. Database: PostgreSQL com multi-tenancy (tenant_id em todos os models)
4. Stack: Python 3.12+, FastAPI, SQLModel, Pydantic v2, React 19, TypeScript strict

ARQUIVOS DE REFERÊNCIA:
- RULES.md (este arquivo) - Regras globais
- PROJECT_GUIDE.md - Checklist completo
- IMPLEMENTATION_PLAN.md - Prompts sequenciais

ANTES DE CODIFICAR:
1. Leia RULES.md completamente
2. Verifique a estrutura de diretórios em PROJECT_GUIDE.md
3. Confirme que está na etapa correta do IMPLEMENTATION_PLAN.md

NUNCA QUEBRE:
- tenant_id em todos os models
- Soft-delete em todos os models
- Pydantic v2 com model_config
- TypeScript strict mode
- Environment variables via .env
```

---

## ⚡ Dicas de Otimização para Agentes de IA

### Para Economizar Tokens

```markdown
1. Referencie arquivos específicos com @filename em vez de colar conteúdo
2. Use este RULES.md como contexto global (leitura única por sessão)
3. Para tarefas grandes, quebre em múltiplos prompts do IMPLEMENTATION_PLAN.md
4. Commit após cada prompt concluído para manter histórico limpo
```

### Para Manter Consistência

```markdown
1. Sempre valide imports após gerar código novo
2. Execute type check antes de considerar tarefa concluída
3. Use `tree -L 3` para verificar estrutura de pastas
4. Compare com PROJECT_GUIDE.md para conformidade
```

### Para Debug

```markdown
1. Use structlog no backend para logs estruturados
2. Use React Query DevTools no frontend
3. Teste webhooks ASAAS com ngrok ou webhook.site
4. Verifique .env sempre que houver erro de configuração
```

---

## 📌 Resumo Rápido (Cheat Sheet)

```yaml
Stack:
  Backend: FastAPI + SQLModel + PostgreSQL + Redis + Celery
  Frontend: React 19 + Vite + TypeScript + Tailwind + shadcn/ui
  Billing: ASAAS
  Email: Brevo
  Auth: JWT

Regras de Ouro:
  - tenant_id em todos os models
  - Soft-delete obrigatório
  - Pydantic v2 (model_config)
  - TypeScript strict
  - .env para secrets
  - Docker para tudo
  - Tests 80%+ coverage

Comandos Chave:
  - make up / make down
  - make migrate / make seed
  - make test-backend / make test-frontend
  - make bootstrap (tudo junto)
```

---

*Este arquivo é IDE-agnóstico e funciona com: Cursor, Windsurf, ClaudeCode, OpenCode, Antigravity, GitHub Copilot, Codex, e qualquer agente de IA com acesso a arquivos.*  
*Versão: 2026.1 | Mantenha este arquivo atualizado com mudanças na stack*