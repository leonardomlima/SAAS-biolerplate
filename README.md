# 🚀 SaaS Boilerplate Pro - Plataforma Completa com IA

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116+-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis)](https://redis.io/)
[![CI/CD](https://github.com/yourorg/saas-boilerplate-pro/actions/workflows/ci.yml/badge.svg)](https://github.com/yourorg/saas-boilerplate-pro/actions)
[![Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen)](#)

> **Boilerplate SaaS production-ready** com FastAPI + React, multi-tenant, billing integrado, emails transacionais e **módulo de IA com Chat, Agentes Especializados e Text2SQL**.

---

## ✨ Destaques

### 🎯 Funcionalidades Core
- ✅ **Multi-tenancy completo** - Isolamento de dados por organização
- ✅ **Auth robusto** - JWT, refresh tokens, OAuth2, reset de senha, convites
- ✅ **RBAC avançado** - Roles (owner, admin, member, viewer) com permissões granulares
- ✅ **Billing integrado** - ASAAS para assinaturas e webhooks
- ✅ **Emails transacionais** - Brevo para notificações e fluxos automatizados
- ✅ **Auditoria completa** - Logs de eventos críticos para compliance

### 🤖 Módulo de IA (Novidade!)
- ✅ **Chat com Agentes** - Conversas contextuais com histórico persistente
- ✅ **Grupos de Modelos** - Reasoning, Creative, Coding, Fast, Balanced
- ✅ **Temperature Inteligente** - Adaptação automática para modelos o1 (reasoning_effort)
- ✅ **20+ Tools Integradas** - Search, SQL, Web, Code, Email, Automation
- ✅ **Text2SQL Seguro** - Análise de dados em linguagem natural com isolamento tenant
- ✅ **Contexto Redis** - Buffer de sessão ativo com LRU para controle de custos
- ✅ **OpenRouter Centralizado** - Acesso a 100+ modelos com uma única API key

### 🛡️ Segurança & Qualidade
- ✅ Rate limiting global e por endpoint crítico
- ✅ Proteção anti brute-force com bloqueio progressivo
- ✅ CORS refinado e headers de segurança (CSP, X-Frame, HSTS)
- ✅ Validação rigorosa com Pydantic v2 e Zod
- ✅ CI/CD completo (lint, type-check, tests, build)
- ✅ Testes unitários (backend) + E2E (Playwright)

---

## 📦 Stack Tecnológico

| Área | Tecnologias |
|------|-------------|
| **Backend** | Python 3.12+, FastAPI 0.116, SQLModel, SQLAlchemy 2.0 (Async), Alembic |
| **Frontend** | React 19, TypeScript 5.9, Vite 6, Tailwind CSS 4, shadcn/ui, Radix UI |
| **State** | Zustand (global), TanStack Query (server state), React Hook Form + Zod |
| **Database** | PostgreSQL 16 (multi-tenant), Redis 7 (cache + sessions) |
| **Task Queue** | Celery 5.5 + Redis Broker (emails, webhooks, background jobs) |
| **IA/LLM** | OpenRouter (100+ modelos), LangChain patterns, Tool calling |
| **Services** | ASAAS (billing), Brevo (email), Sentry (monitoring) |
| **Infra** | Docker, Docker Compose, GitHub Actions, Ready for Render/Railway/Fly.io |

---

## 🚀 Quickstart

### Pré-requisitos
```bash
# Docker e Docker Compose instalados
# Node.js 20+ (para desenvolvimento frontend local)
# Python 3.12+ (opcional, para desenvolvimento backend local)
```

### 1. Clone e Setup Inicial
```bash
git clone https://github.com/yourorg/saas-boilerplate-pro.git
cd saas-boilerplate-pro

# Copie o arquivo de exemplo
cp .env.example .env

# Gere uma SECRET_KEY segura
openssl rand -hex 32
# Cole no .env: SECRET_KEY=seu_valor_aqui
```

### 2. Configure Variáveis de Ambiente
Edite `.env` com suas credenciais:

```bash
# Backend
SECRET_KEY=your_secret_key_here
DATABASE_URL=postgresql://postgres:postgres@db:5432/saas_boilerplate
REDIS_URL=redis://redis:6379/0

# OpenRouter (obrigatório para funcionalidades de IA)
OPENROUTER_API_KEY=sk_or_xxxxxxxxxxxxx

# Billing (ASAAS)
ASAAS_API_KEY=xxxxx
ASAAS_WEBHOOK_TOKEN=xxxxx

# Email (Brevo)
BREVO_API_KEY=xxxxx
EMAIL_FROM=noreply@yourdomain.com

# Frontend URL
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000
```

### 3. Suba os Serviços
```bash
# Build e start de todos os serviços
docker-compose up -d --build

# Aguarde ~30s para PostgreSQL e Redis estarem prontos
```

### 4. Execute Migrations e Seed
```bash
# Criar tabelas no banco
docker-compose exec backend alembic upgrade head

# Popular com dados de exemplo (opcional)
docker-compose exec backend python -m app.scripts.seed_data
```

### 5. Acesse a Aplicação
```
Frontend: http://localhost:5173
Backend API: http://localhost:8000
API Docs (Swagger): http://localhost:8000/docs
```

**Credenciais de teste (seed):**
- Email: `admin@example.com`
- Senha: `password123`

---

## 📚 Documentação

### Guias Principais
| Documento | Descrição |
|-----------|-----------|
| [GETTING_STARTED.md](./docs/GETTING_STARTED.md) | Guia passo-a-passo para primeiros passos |
| [ARCHITECTURE.md](./docs/ARCHITECTURE.md) | Visão geral da arquitetura e decisões técnicas |
| [DEPLOYMENT.md](./docs/DEPLOYMENT.md) | Deploy em produção (Render, Railway, Fly.io) |
| [CONTRIBUTING.md](./docs/CONTRIBUTING.md) | Como contribuir com o projeto |
| [OPERATIONS.md](./docs/OPERATIONS.md) | Operações diárias, monitoring e troubleshooting |

### Módulos Específicos
| Documento | Descrição |
|-----------|-----------|
| [AI_MODULE.md](./docs/AI_MODULE.md) | Uso do módulo de IA, agentes e Text2SQL |
| [BILLING_SETUP.md](./docs/BILLING_SETUP.md) | Configuração do ASAAS para billing |
| [EMAIL_SETUP.md](./docs/EMAIL_SETUP.md) | Configuração do Brevo para emails |

---

## 🤖 Módulo de IA - Guia Rápido

### Criando seu Primeiro Agente

```python
from uuid import UUID
from app.models.agent import AgentType, ModelProvider, ReasoningEffort

# Agente de Chat Geral
agent_chat = {
    "name": "Assistente Geral",
    "agent_type": AgentType.CHAT,
    "model_name": "openai/gpt-4o-mini",
    "model_group": "balanced",
    "temperature": 0.7,
    "enabled_tools": ["search_knowledge_base", "get_user_profile"],
}

# Agente de Raciocínio Complexo
agent_reasoning = {
    "name": "Analista de Dados",
    "agent_type": AgentType.TEXT2SQL,
    "model_name": "openai/o1-pro",
    "model_group": "reasoning",
    "reasoning_effort": ReasoningEffort.HIGH,
    "reasoning_summary": True,
    "allowed_tables": ["users", "subscriptions", "payments"],
    "read_only": True,
}

# Agente de Código
agent_coding = {
    "name": "Code Assistant",
    "agent_type": AgentType.CHAT,
    "model_name": "deepseek/deepseek-coder-v2",
    "model_group": "coding",
    "temperature": 0.2,
    "enabled_tools": ["generate_code_snippet", "debug_error_log"],
}
```

### Tools Disponíveis (20+)

#### Produtividade & Dados
1. `search_knowledge_base` - Busca na base de conhecimento da organização
2. `query_database_sql` - Executa queries SQL seguras (somente leitura)
3. `get_user_profile` - Obtém perfil do usuário atual
4. `list_organization_members` - Lista membros da organização
5. `fetch_webhook_logs` - Busca logs de webhooks de billing

#### Web & Pesquisa
6. `web_search` - Pesquisa na web via DuckDuckGo/SerpAPI
7. `scrape_website` - Extrai conteúdo de URLs
8. `check_competitor_pricing` - Monitora preços de concorrentes
9. `translate_text` - Traduz entre 100+ idiomas
10. `summarize_url` - Resume artigos e páginas web

#### Criação & Desenvolvimento
11. `generate_code_snippet` - Gera código em múltiplas linguagens
12. `debug_error_log` - Analisa logs de erro e sugere fixes
13. `create_html_email` - Cria templates HTML para emails
14. `generate_survey_questions` - Gera perguntas para pesquisas
15. `seo_analyzer` - Analisa SEO de páginas web

#### Automação & Ação
16. `send_email_draft` - Envia rascunho de email via Brevo
17. `create_calendar_event` - Cria eventos no Google Calendar
18. `calculate_financials` - Realiza cálculos financeiros complexos
19. `generate_image_prompt` - Cria prompts para DALL-E/Midjourney
20. `sentiment_analysis` - Analisa sentimento de textos

### Exemplo: Análise de Dados com Text2SQL

```python
# POST /api/v1/ai/text2sql
{
    "question": "Qual o MRR total por plano nos últimos 3 meses?",
    "agent_id": "uuid-do-agente-text2sql",
    "session_id": "uuid-da-sessao-opcional"
}

# Resposta:
{
    "question": "Qual o MRR total por plano nos últimos 3 meses?",
    "sql_query": "SELECT p.name, SUM(s.amount) as mrr FROM subscriptions s JOIN plans p ON s.plan_id = p.id WHERE s.status = 'active' AND s.created_at >= NOW() - INTERVAL '3 months' AND s.tenant_id = 'xxx' GROUP BY p.name",
    "results": [
        {"name": "Basic", "mrr": 1500.00},
        {"name": "Pro", "mrr": 4500.00},
        {"name": "Enterprise", "mrr": 12000.00}
    ],
    "explanation": "Query calcula MRR somando valores de assinaturas ativas dos últimos 3 meses, agrupadas por plano",
    "columns": ["name", "mrr"]
}
```

### Grupos de Modelos Recomendados

| Grupo | Casos de Uso | Modelos Sugeridos | Temperature/Reasoning |
|-------|--------------|-------------------|----------------------|
| **Reasoning** | Análise complexa, matemática, planejamento | o1-pro, o1-mini, Claude 3.7 Thinking, DeepSeek R1 | reasoning_effort: high |
| **Creative** | Copywriting, marketing, brainstorming | GPT-4o, Claude 3.5 Sonnet, Gemini Pro 1.5 | temperature: 0.8 |
| **Coding** | Programação, code review, debug | DeepSeek Coder V2, GPT-4 Turbo, Qwen 2.5 Coder | temperature: 0.2 |
| **Fast** | Tarefas simples, alto volume, classificação | Llama 3 8B, Gemma 7B, Mistral 7B, GPT-3.5 Turbo | temperature: 0.5 |
| **Balanced** | Chatbots gerais, uso diário | GPT-4o Mini, Claude 3 Haiku, Gemini Flash 1.5 | temperature: 0.7 |

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React 19)                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │
│  │   Auth   │ │ Dashboard│ │   Chat   │ │  Text2SQL    │   │
│  │  Pages   │ │  Pages   │ │  Module  │ │   Module     │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘   │
│         │              │              │                     │
│         └──────────────┴──────────────┘                     │
│                         │                                   │
│                  TanStack Query                             │
│                  Zustand State                              │
└─────────────────────────┼───────────────────────────────────┘
                          │ HTTP/REST + WebSocket
┌─────────────────────────┼───────────────────────────────────┐
│                   Backend (FastAPI)         │               │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │  API Routes  │ │   Services   │ │   CRUD       │        │
│  │  (v1/endpoints)│ │ (LLM, Email, │ │ (SQLModel)  │        │
│  │              │ │  Billing)    │ │             │        │
│  └──────────────┘ └──────────────┘ └──────────────┘        │
│         │                                       │           │
│  ┌──────┴──────────┐                   ┌────────┴──────┐    │
│  │  Auth Middleware │                   │ Task Queue    │    │
│  │  (JWT + RBAC)    │                   │ (Celery)      │    │
│  └─────────────────┘                   └───────────────┘    │
└──────────┼────────────────────────────────────┬─────────────┘
           │                                    │
┌──────────┼────────────┐          ┌────────────┴──────────┐  │
│    PostgreSQL 16      │          │      Redis 7          │  │
│  ┌─────────────────┐  │          │  ┌─────────────────┐  │  │
│  │ Multi-Tenant DB │  │          │  │ Cache + Sessions│  │  │
│  │ - users         │  │          │  │ - Chat Context  │  │  │
│  │ - organizations │  │          │  │ - Rate Limiting │  │  │
│  │ - agents        │  │          │  │ - Celery Broker │  │  │
│  │ - chat_sessions │  │          │  └─────────────────┘  │  │
│  │ - messages      │  │          └───────────────────────┘  │
│  └─────────────────┘  │                                      │
└───────────────────────┘
           │
┌──────────┼───────────────────────────────────────┐
│          │         External Services              │
│  ┌───────┴──────┐  ┌─────────────┐  ┌──────────┐ │
│  │ OpenRouter   │  │   ASAAS     │  │  Brevo   │ │
│  │ (100+ LLMs)  │  │  (Billing)  │  │ (Email)  │ │
│  └──────────────┘  └─────────────┘  └──────────┘ │
└──────────────────────────────────────────────────┘
```

---

## 🧪 Testes

### Backend (Pytest)
```bash
# Rodar todos os testes
docker-compose exec backend pytest

# Com coverage
docker-compose exec backend pytest --cov=app --cov-report=html

# Testes específicos
docker-compose exec backend pytest tests/test_ai_module.py -v
```

### Frontend (Vitest + Playwright)
```bash
# Unit tests
cd frontend && npm run test

# E2E tests
cd frontend && npm run test:e2e

# E2E com UI
cd frontend && npm run test:e2e -- --ui
```

### CI/CD
O projeto inclui workflows automáticos no GitHub Actions:
- **CI Backend**: Install → Type Check → Lint → Tests → Coverage
- **CI Frontend**: Install → Type Check → Lint → Build
- **E2E**: Spin up docker → Seed data → Run Playwright tests

---

## 📊 Roadmap

### ✅ Entregue (Fases 1-4 + IA)
- [x] Setup completo do projeto
- [x] Estrutura base multi-tenant
- [x] Frontend production-ready (auth, orgs, billing)
- [x] Segurança, qualidade e operação
- [x] **Módulo de IA com Chat e Agentes**
- [x] **Text2SQL para análise de dados**
- [x] **20+ tools integradas**
- [x] **Grupos de modelos especializados**

### 🚧 Em Desenvolvimento
- [ ] Painel de formulários de pesquisa
- [ ] Builder de HTML simplificado
- [ ] Campanhas de email marketing
- [ ] Dashboards de analytics de IA
- [ ] Custom branding white-label

### 📋 Planejado
- [ ] Integração com mais provedores de LLM (Anthropic direto, Google Vertex)
- [ ] Fine-tuning de modelos customizados
- [ ] RAG (Retrieval Augmented Generation) com vector database
- [ ] Marketplace de agents pré-configurados
- [ ] Exportação de dados em múltiplos formatos

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Veja nosso guia completo em [CONTRIBUTING.md](./docs/CONTRIBUTING.md).

### Passos Rápidos
```bash
# Fork o repositório
git clone https://github.com/SEU_USER/saas-boilerplate-pro.git

# Crie uma branch para sua feature
git checkout -b feature/minha-feature

# Faça commit das mudanças
git commit -m 'feat: adiciona minha feature'

# Push e crite um PR
git push origin feature/minha-feature
```

### Padrões do Projeto
- **Commits**: Seguir [Conventional Commits](https://www.conventionalcommits.org/)
- **Código**: Seguir lint configs (`.pre-commit-config.yaml`)
- **Testes**: Cobertura mínima de 80% para novas features
- **Docs**: Atualizar README e docs relevantes

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja [LICENSE](./LICENSE) para detalhes.

---

## 🙏 Agradecimentos

- [FastAPI](https://fastapi.tiangolo.com/) pelo framework incrível
- [React](https://react.dev/) pela biblioteca que revolucionou o frontend
- [shadcn/ui](https://ui.shadcn.com/) pelos componentes lindos e acessíveis
- [OpenRouter](https://openrouter.ai/) pela centralização de modelos de IA
- [ASAAS](https://asaas.com/) e [Brevo](https://brevo.com/) pelas integrações essenciais

---

## 📞 Suporte & Comunidade

- **Issues**: [GitHub Issues](https://github.com/yourorg/saas-boilerplate-pro/issues)
- **Discord**: [Entre na comunidade](https://discord.gg/xxxxx)
- **Email**: support@saasboilerplate.pro
- **Documentação**: [Docs completos](https://docs.saasboilerplate.pro)

---

<div align="center">

**Feito com ❤️ para acelerar seu próximo SaaS**

[⭐ Star no GitHub](https://github.com/yourorg/saas-boilerplate-pro) • [📖 Docs](https://docs.saasboilerplate.pro) • [💬 Discord](https://discord.gg/xxxxx)

</div>

