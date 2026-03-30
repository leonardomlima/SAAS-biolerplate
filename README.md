# SaaS Boilerplate

![Docker](https://img.shields.io/badge/Docker-ready-2496ED)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116-009688)
![React](https://img.shields.io/badge/React-19-61DAFB)
![ASAAS](https://img.shields.io/badge/Billing-ASAAS-4E7CF2)
![Brevo](https://img.shields.io/badge/Email-Brevo-0B996E)

Boilerplate SaaS com **FastAPI + React**, multi-tenant, billing ASAAS e emails transacionais via Brevo.

## Quickstart

```bash
make up
make migrate
make seed
```

## Fase 3 entregue (Frontend de produção)

- Formulários de login, registro, reset e organizações com **React Hook Form + Zod**.
- Estados de loading/erro e feedback por toast (`sonner`).
- Rotas protegidas com fluxo de sessão (token + tenant persistidos no `localStorage`).
- Telas de billing e organizações conectadas à API real.

## Fase 4 entregue (Qualidade, segurança e operação)

### Segurança
- Rate limit global e por endpoint crítico de auth (login/register/reset/refresh).
- Proteção básica anti brute-force por tentativas falhas de login.
- Auditoria de eventos críticos (auth e billing webhook/checkout).
- Hardening de headers HTTP (CSP, X-Frame-Options, nosniff, etc).
- CORS refinado (origens/métodos/headers explícitos).

### Qualidade/CI
- CI frontend validando install + lint + build.
- CI backend validando install + type-check + tests.
- Testes expandidos para segurança e jornada de autenticação (backend + e2e frontend).

### Operação
- Ver `docs/OPERATIONS.md` para execução local, configuração de providers, webhooks e checklist de deploy.

## B2B/B2C

Para B2C, mantenha tenant único e desative TenantSwitch.
