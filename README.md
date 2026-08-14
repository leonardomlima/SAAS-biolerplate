# SaaS Boilerplate Pro - Production-Ready Platform with AI

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116+-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis)](https://redis.io/)
[![CI/CD](https://github.com/yourorg/saas-boilerplate-pro/actions/workflows/ci.yml/badge.svg)](https://github.com/yourorg/saas-boilerplate-pro/actions)
[![Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen)](#)

**Production-ready SaaS boilerplate** built with FastAPI and React, featuring multi-tenancy, integrated billing, transactional emails, and an advanced AI module with Chat, Specialized Agents, and Text2SQL capabilities.

---

## Key Features

### Core Functionality
- **Complete Multi-tenancy** - Data isolation by organization
- **Robust Authentication** - JWT, refresh tokens, OAuth2, password reset, invitations
- **Advanced RBAC** - Roles (owner, admin, member, viewer) with granular permissions
- **Integrated Billing** - ASAAS for subscriptions and webhooks
- **Transactional Emails** - Brevo for notifications and automated flows
- **Complete Audit Trail** - Critical event logging for compliance

### AI Module
- **Chat with Agents** - Contextual conversations with persistent history
- **Model Groups** - Reasoning, Creative, Coding, Fast, Balanced
- **Intelligent Temperature** - Automatic adaptation for o1 models (reasoning_effort)
- **20+ Integrated Tools** - Search, SQL, Web, Code, Email, Automation
- **Secure Text2SQL** - Natural language data analysis with tenant isolation
- **Redis Context** - Active session buffer with LRU for cost control
- **OpenRouter Centralized** - Access to 100+ models with a single API key

### Security & Quality
- Global and per-endpoint rate limiting
- Anti brute-force protection with progressive blocking
- Refined CORS and security headers (CSP, X-Frame, HSTS)
- Rigorous validation with Pydantic v2 and Zod
- Complete CI/CD (lint, type-check, tests, build)
- Unit tests (backend) + E2E (Playwright)

---

## Technology Stack

| Area | Technologies |
|------|-------------|
| **Backend** | Python 3.12+, FastAPI 0.116, SQLModel, SQLAlchemy 2.0 (Async), Alembic |
| **Frontend** | React 19, TypeScript 5.9, Vite 6, Tailwind CSS 4, shadcn/ui, Radix UI |
| **State** | Zustand (global), TanStack Query (server state), React Hook Form + Zod |
| **Database** | PostgreSQL 16 (multi-tenant), Redis 7 (cache + sessions) |
| **Task Queue** | Celery 5.5 + Redis Broker (emails, webhooks, background jobs) |
| **AI/LLM** | OpenRouter (100+ models), LangChain patterns, Tool calling |
| **Services** | ASAAS (billing), Brevo (email), Sentry (monitoring) |
| **Infra** | Docker, Docker Compose, GitHub Actions, Ready for Render/Railway/Fly.io |

---

## Quickstart

### Prerequisites
```bash
# Docker and Docker Compose installed
# Node.js 20+ (for local frontend development)
# Python 3.12+ (optional, for local backend development)
```

### 1. Clone and Initial Setup
```bash
git clone https://github.com/yourorg/saas-boilerplate-pro.git
cd saas-boilerplate-pro

# Copy example file
cp .env.example .env

# Generate a secure SECRET_KEY
openssl rand -hex 32
# Paste to .env: SECRET_KEY=your_value_here
```

### 2. Configure Environment Variables
Edit `.env` with your credentials:

```bash
# Backend
SECRET_KEY=your_secret_key_here
DATABASE_URL=postgresql://postgres:postgres@db:5432/saas_boilerplate
REDIS_URL=redis://redis:6379/0

# OpenRouter (required for AI features)
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

### 3. Start Services
```bash
# Build and start all services
docker-compose up -d --build

# Wait ~30s for PostgreSQL and Redis to be ready
```

### 4. Run Migrations and Seed
```bash
# Create tables in database
docker-compose exec backend alembic upgrade head

# Populate with sample data (optional)
docker-compose exec backend python -m app.scripts.seed_data
```

### 5. Access the Application
```
Frontend: http://localhost:5173
Backend API: http://localhost:8000
API Docs (Swagger): http://localhost:8000/docs
```

**Test credentials (seed):**
- Email: `admin@example.com`
- Password: `password123`

---

## Documentation

### Main Guides
| Document | Description |
|-----------|-----------|
| [GETTING_STARTED.md](./docs/GETTING_STARTED.md) | Step-by-step guide for getting started |
| [ARCHITECTURE.md](./docs/ARCHITECTURE.md) | Architecture overview and technical decisions |
| [DEPLOYMENT.md](./docs/DEPLOYMENT.md) | Production deployment (Render, Railway, Fly.io) |
| [CONTRIBUTING.md](./docs/CONTRIBUTING.md) | How to contribute to the project |
| [OPERATIONS.md](./docs/OPERATIONS.md) | Daily operations, monitoring and troubleshooting |

### Specific Modules
| Document | Description |
|-----------|-----------|
| [AI_MODULE.md](./docs/AI_MODULE.md) | Using the AI module, agents and Text2SQL |
| [BILLING_SETUP.md](./docs/BILLING_SETUP.md) | ASAAS configuration for billing |
| [EMAIL_SETUP.md](./docs/EMAIL_SETUP.md) | Brevo configuration for emails |

---

## AI Module - Quick Guide

### Creating Your First Agent

```python
from uuid import UUID
from app.models.agent import AgentType, ModelProvider, ReasoningEffort

# General Chat Agent
agent_chat = {
    "name": "General Assistant",
    "agent_type": AgentType.CHAT,
    "model_name": "openai/gpt-4o-mini",
    "model_group": "balanced",
    "temperature": 0.7,
    "enabled_tools": ["search_knowledge_base", "get_user_profile"],
}

# Complex Reasoning Agent
agent_reasoning = {
    "name": "Data Analyst",
    "agent_type": AgentType.TEXT2SQL,
    "model_name": "openai/o1-pro",
    "model_group": "reasoning",
    "reasoning_effort": ReasoningEffort.HIGH,
    "reasoning_summary": True,
    "allowed_tables": ["users", "subscriptions", "payments"],
    "read_only": True,
}

# Coding Agent
agent_coding = {
    "name": "Code Assistant",
    "agent_type": AgentType.CHAT,
    "model_name": "deepseek/deepseek-coder-v2",
    "model_group": "coding",
    "temperature": 0.2,
    "enabled_tools": ["generate_code_snippet", "debug_error_log"],
}
```

### Available Tools (20+)

#### Productivity & Data
1. `search_knowledge_base` - Search organization knowledge base
2. `query_database_sql` - Execute safe SQL queries (read-only)
3. `get_user_profile` - Get current user profile
4. `list_organization_members` - List organization members
5. `fetch_webhook_logs` - Fetch billing webhook logs

#### Web & Research
6. `web_search` - Web search via DuckDuckGo/SerpAPI
7. `scrape_website` - Extract content from URLs
8. `check_competitor_pricing` - Monitor competitor pricing
9. `translate_text` - Translate between 100+ languages
10. `summarize_url` - Summarize articles and web pages

#### Creation & Development
11. `generate_code_snippet` - Generate code in multiple languages
12. `debug_error_log` - Analyze error logs and suggest fixes
13. `create_html_email` - Create HTML email templates
14. `generate_survey_questions` - Generate survey questions
15. `seo_analyzer` - Analyze web page SEO

#### Automation & Action
16. `send_email_draft` - Send email drafts via Brevo
17. `create_calendar_event` - Create Google Calendar events
18. `calculate_financials` - Perform complex financial calculations
19. `generate_image_prompt` - Create prompts for DALL-E/Midjourney
20. `sentiment_analysis` - Analyze text sentiment

### Example: Data Analysis with Text2SQL

```python
# POST /api/v1/ai/text2sql
{
    "question": "What is the total MRR by plan in the last 3 months?",
    "agent_id": "uuid-of-text2sql-agent",
    "session_id": "optional-session-uuid"
}

# Response:
{
    "question": "What is the total MRR by plan in the last 3 months?",
    "sql_query": "SELECT p.name, SUM(s.amount) as mrr FROM subscriptions s JOIN plans p ON s.plan_id = p.id WHERE s.status = 'active' AND s.created_at >= NOW() - INTERVAL '3 months' AND s.tenant_id = 'xxx' GROUP BY p.name",
    "results": [
        {"name": "Basic", "mrr": 1500.00},
        {"name": "Pro", "mrr": 4500.00},
        {"name": "Enterprise", "mrr": 12000.00}
    ],
    "explanation": "Query calculates MRR by summing active subscription values from the last 3 months, grouped by plan",
    "columns": ["name", "mrr"]
}
```

### Recommended Model Groups

| Group | Use Cases | Suggested Models | Temperature/Reasoning |
|-------|-----------|------------------|----------------------|
| **Reasoning** | Complex analysis, math, planning | o1-pro, o1-mini, Claude 3.7 Thinking, DeepSeek R1 | reasoning_effort: high |
| **Creative** | Copywriting, marketing, brainstorming | GPT-4o, Claude 3.5 Sonnet, Gemini Pro 1.5 | temperature: 0.8 |
| **Coding** | Programming, code review, debug | DeepSeek Coder V2, GPT-4 Turbo, Qwen 2.5 Coder | temperature: 0.2 |
| **Fast** | Simple tasks, high volume, classification | Llama 3 8B, Gemma 7B, Mistral 7B, GPT-3.5 Turbo | temperature: 0.5 |
| **Balanced** | General chatbots, daily use | GPT-4o Mini, Claude 3 Haiku, Gemini Flash 1.5 | temperature: 0.7 |

---

## Architecture

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

## Testing

### Backend (Pytest)
```bash
# Run all tests
docker-compose exec backend pytest

# With coverage
docker-compose exec backend pytest --cov=app --cov-report=html

# Specific tests
docker-compose exec backend pytest tests/test_ai_module.py -v
```

### Frontend (Vitest + Playwright)
```bash
# Unit tests
cd frontend && npm run test

# E2E tests
cd frontend && npm run test:e2e

# E2E with UI
cd frontend && npm run test:e2e -- --ui
```

### CI/CD
The project includes automated workflows in GitHub Actions:
- **CI Backend**: Install → Type Check → Lint → Tests → Coverage
- **CI Frontend**: Install → Type Check → Lint → Build
- **E2E**: Spin up docker → Seed data → Run Playwright tests

---

## Roadmap

### ✅ Delivered (Phases 1-4 + AI)
- [x] Complete project setup
- [x] Multi-tenant base structure
- [x] Production-ready frontend (auth, orgs, billing)
- [x] Security, quality and operations
- [x] **AI Module with Chat and Agents**
- [x] **Text2SQL for data analysis**
- [x] **20+ integrated tools**
- [x] **Specialized model groups**

### 🚧 In Development
- [ ] Survey form builder panel
- [ ] Simplified HTML builder
- [ ] Email marketing campaigns
- [ ] AI analytics dashboards
- [ ] Custom branding white-label

### 📋 Planned
- [ ] Integration with more LLM providers (Anthropic direct, Google Vertex)
- [ ] Fine-tuning of custom models
- [ ] RAG (Retrieval Augmented Generation) with vector database
- [ ] Marketplace of pre-configured agents
- [ ] Data export in multiple formats

---

## Contributing

Contributions are welcome! See our complete guide at [CONTRIBUTING.md](./docs/CONTRIBUTING.md).

### Quick Steps
```bash
# Fork the repository
git clone https://github.com/YOUR_USER/saas-boilerplate-pro.git

# Create a branch for your feature
git checkout -b feature/my-feature

# Commit changes
git commit -m 'feat: add my feature'

# Push and create a PR
git push origin feature/my-feature
```

### Project Standards
- **Commits**: Follow [Conventional Commits](https://www.conventionalcommits.org/)
- **Code**: Follow lint configs (`.pre-commit-config.yaml`)
- **Tests**: Minimum 80% coverage for new features
- **Docs**: Update README and relevant docs

---

## License

This project is under the MIT license. See [LICENSE](./LICENSE) for details.

---

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the amazing framework
- [React](https://react.dev/) for the library that revolutionized frontend
- [shadcn/ui](https://ui.shadcn.com/) for beautiful and accessible components
- [OpenRouter](https://openrouter.ai/) for centralizing AI models
- [ASAAS](https://asaas.com/) and [Brevo](https://brevo.com/) for essential integrations

---

## Support & Community

- **Issues**: [GitHub Issues](https://github.com/yourorg/saas-boilerplate-pro/issues)
- **Discord**: [Join the community](https://discord.gg/xxxxx)
- **Email**: support@saasboilerplate.pro
- **Documentation**: [Full docs](https://docs.saasboilerplate.pro)

---

<div align="center">

**Built with care to accelerate your next SaaS**

[Star on GitHub](https://github.com/yourorg/saas-boilerplate-pro) • [Docs](https://docs.saasboilerplate.pro) • [Discord](https://discord.gg/xxxxx)

</div>

