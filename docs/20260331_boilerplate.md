# SaaS Boilerplate - Complete Technical Documentation

**Generated:** 2026-03-31  
**Version:** 0.1.0  
**Status:** Development/Pre-Production

---

## 1. Project Overview

This is a multi-tenant SaaS boilerplate built with FastAPI (backend) and React/TypeScript (frontend). It provides a foundational architecture for building Software-as-a-Service applications with built-in support for authentication, multi-tenancy, billing (via Asaas), email notifications (via Brevo), and background task processing (via Celery).

**Technology Stack:**

- **Backend:** FastAPI 0.109+, Python 3.13, SQLModel, AsyncPG
- **Frontend:** React 18, TypeScript, Vite, TailwindCSS
- **Database:** PostgreSQL 16 (async)
- **Cache/Queue:** Redis 7
- **Task Queue:** Celery
- **Authentication:** JWT with refresh tokens
- **Payment Processing:** Asaas (Brazilian payment gateway)
- **Email Service:** Brevo (formerly Sendinblue)

---

## 2. Directory Structure

```
boilerplate_v01/
├── .env                          # Environment variables (do not commit)
├── .env.example                  # Template for environment variables
├── .gitignore
├── README.md
├── Makefile                      # Development commands
├── docker-compose.yml           # Production compose
├── docker-compose.dev.yml       # Development compose
├── Dockerfile.backend
├── Dockerfile.frontend
├── Dockerfile.frontend-dev
├── render.yaml                   # Render.com deployment config
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application entry point
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── __init__.py  # API router aggregation
│   │   │       ├── api_router.py
│   │   │       ├── endpoints/
│   │   │       │   ├── __init__.py
│   │   │       │   ├── auth.py         # Authentication endpoints
│   │   │       │   ├── users.py        # User management
│   │   │       │   ├── organizations.py # Organization CRUD
│   │   │       │   ├── billing.py       # Subscription/payment
│   │   │       │   ├── health.py        # Health checks
│   │   │       │   └── core_feature.py  # Feature flags demo
│   │   │       └── dependencies/
│   │   │           ├── __init__.py
│   │   │           ├── current_user.py # JWT validation
│   │   │           └── current_tenant.py # Tenant isolation
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py          # Settings management (Pydantic)
│   │   │   ├── database.py       # SQLModel async engine setup
│   │   │   ├── security.py        # JWT/password utilities
│   │   │   ├── tenant.py         # Multi-tenant middleware
│   │   │   ├── cache.py          # Redis cache (stub implementation)
│   │   │   ├── limiter.py        # Rate limiting (slowapi)
│   │   │   └── security_headers.py # CSP/X-Frame headers
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py           # BaseModel with tenant_id, timestamps
│   │   │   ├── user.py           # User entity
│   │   │   ├── organization.py   # Organization entity
│   │   │   ├── subscription.py   # Subscription/billing
│   │   │   ├── asaas_customer.py # Asaas customer mapping
│   │   │   ├── asaas_webhook_event.py # Webhook events log
│   │   │   ├── audit_log.py      # Audit trail
│   │   │   ├── email_delivery.py # Email tracking
│   │   │   └── feature_flag.py   # Feature toggles
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py           # Auth DTOs (Login, Register, etc.)
│   │   │   ├── user.py           # User DTOs
│   │   │   ├── organization.py   # Organization DTOs
│   │   │   ├── billing.py        # Billing DTOs
│   │   │   └── response.py       # Generic responses
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── asaas_service.py  # Asaas API integration
│   │   │   ├── email_service.py # Brevo API integration
│   │   │   ├── audit_service.py # Audit log writer
│   │   │   └── feature_flag_service.py
│   │   │
│   │   ├── crud/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── user.py
│   │   │   ├── organization.py
│   │   │   └── subscription.py
│   │   │
│   │   ├── background/
│   │   │   └── tasks.py          # Celery tasks
│   │   │
│   │   └── utils/
│   │       └── pagination.py
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py           # Pytest fixtures
│   │   ├── test_auth.py
│   │   ├── test_users.py
│   │   ├── test_organizations.py
│   │   ├── test_billing.py
│   │   ├── test_security_headers.py
│   │   └── test_auth_rate_limit.py
│   │
│   ├── alembic/
│   │   ├── env.py               # Alembic configuration
│   │   ├── script.py.mako
│   │   └── versions/
│   │       └── 20260330_0001_phase2_saas_integrations.py
│   │
│   ├── pyproject.toml           # Poetry dependencies
│   └── poetry.lock
│
├── frontend/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── vite-env.d.ts
│   │   ├── types/
│   │   │   └── index.ts         # TypeScript interfaces
│   │   ├── lib/
│   │   │   └── api.ts           # Axios API client
│   │   ├── hooks/
│   │   │   ├── useAuth.tsx
│   │   │   ├── useTenant.tsx
│   │   │   └── useApi.tsx
│   │   └── store/
│   │       ├── authStore.ts     # Zustand auth state
│   │       └── tenantStore.ts
│   │
│   ├── tests/
│   │   └── e2e/
│   │       ├── auth.spec.ts
│   │       ├── dashboard.spec.ts
│   │       └── billing.spec.ts
│   │
│   ├── public/
│   │   ├── logo.svg
│   │   └── favicon.ico
│   │
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── postcss.config.js
│   ├── eslint.config.js
│   └── playwright.config.ts
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── MULTI_TENANCY.md
│   ├── ASAAS_INTEGRATION.md
│   ├── BREVO_INTEGRATION.md
│   ├── OPERATIONS.md
│   ├── IMPLEMENTATION_PLAN.md
│   ├── PROJECT_GUIDE.md
│   └── RULES.md
│
├── infra/
│   └── scripts/
│       └── seed_db.py
│
└── .github/
    └── workflows/
        ├── ci-backend.yml
        ├── ci-frontend.yml
        ├── docker-publish.yml
        └── deploy.yml
```

---

## 3. Database Schema

### 3.1 Base Model (All Tables Inherit)

Every table inherits from `BaseModel` which provides:

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key, auto-generated |
| tenant_id | UUID | **Critical:** Multi-tenant isolation key |
| is_deleted | boolean | Soft delete flag |
| created_at | datetime | Creation timestamp (UTC) |
| updated_at | datetime | Last update timestamp (UTC) |

### 3.2 Entity Relationship Diagram

```
Organization (1) ──────< User
Organization (1) ──────< Subscription
Organization (1) ──────< AsaasCustomer
Organization (1) ──────< AsaasWebhookEvent
Organization (1) ──────< AuditLog
```

### 3.3 Table Definitions

#### organization

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Same as tenant_id |
| tenant_id | UUID | INDEX | Foreign key to itself |
| name | str | INDEX | Organization name |
| is_deleted | bool | DEFAULT false | Soft delete |
| created_at | datetime | | |
| updated_at | datetime | | |

#### user

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | **Tenant isolation** |
| organization_id | UUID | FK (organization.id) | Owning organization |
| email | str | UNIQUE, INDEX | User email |
| full_name | str | NULLABLE | Display name |
| hashed_password | str | NOT NULL | Bcrypt hash |
| role | str | INDEX, DEFAULT "member" | member, admin, owner |
| is_active | bool | DEFAULT true | Account active status |
| email_verified | bool | DEFAULT false | Email verified |
| reset_password_token | str | NULLABLE | Password reset token |
| reset_password_expires_at | datetime | NULLABLE | Token expiry |
| email_verification_token | str | NULLABLE | Email verification token |
| refresh_token_version | int | DEFAULT 0 | Token revocation counter |
| last_login_at | datetime | NULLABLE | Last login timestamp |
| is_deleted | bool | DEFAULT false | Soft delete |
| created_at | datetime | | |
| updated_at | datetime | | |

#### subscription

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | **Tenant isolation** |
| organization_id | UUID | FK, INDEX | Owning organization |
| asaas_customer_id | str | NULLABLE, INDEX | Asaas customer ID |
| asaas_subscription_id | str | NULLABLE, UNIQUE, INDEX | Asaas subscription ID |
| plan_id | str | INDEX | starter, growth, scale |
| status | str | INDEX, DEFAULT "PENDING" | PENDING, ACTIVE, CANCELED |
| value | float | DEFAULT 0 | Plan price |
| billing_cycle | str | DEFAULT "MONTHLY" | Billing frequency |
| next_due_date | date | NULLABLE | Next payment date |
| activated_at | datetime | NULLABLE | Subscription start |
| canceled_at | datetime | NULLABLE | Subscription end |
| last_synced_at | datetime | | Last Asaas sync |
| is_deleted | bool | DEFAULT false | Soft delete |
| created_at | datetime | | |
| updated_at | datetime | | |

#### asaas_customer

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | **Tenant isolation** |
| organization_id | UUID | FK, INDEX | Owning organization |
| asaas_customer_id | str | UNIQUE, INDEX | Asaas customer ID |
| name | str | | Customer name |
| email | str | | Customer email |
| cpf_cnpj | str | NULLABLE | CPF or CNPJ |
| is_deleted | bool | DEFAULT false | Soft delete |
| created_at | datetime | | |
| updated_at | datetime | | |

#### asaas_webhook_event

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | **Tenant isolation** |
| organization_id | UUID | FK, INDEX, NULLABLE | Owning organization |
| event | str | INDEX | Event type (PAYMENT_RECEIVED, etc.) |
| external_id | str | NULLABLE, UNIQUE, INDEX | Asaas event ID |
| payload | JSON | | Raw event payload |
| processed_at | datetime | NULLABLE | Processing completion |
| processing_status | str | INDEX, DEFAULT "pending" | pending, processed, failed |
| failure_reason | str | NULLABLE | Error message |
| received_at | datetime | | Event received time |
| is_deleted | bool | DEFAULT false | Soft delete |
| created_at | datetime | | |
| updated_at | datetime | | |

#### audit_log

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | **Tenant isolation** |
| actor_user_id | UUID | NULLABLE | User who performed action |
| action | str | INDEX | Action identifier (auth.login, etc.) |
| entity_type | str | | Entity type (user, subscription, etc.) |
| entity_id | str | | Entity UUID |
| details | str | NULLABLE | Additional context (JSON string) |
| is_deleted | bool | DEFAULT false | Soft delete |
| created_at | datetime | | |
| updated_at | datetime | | |

#### email_delivery

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | **Tenant isolation** |
| template_key | str | INDEX | welcome, reset, invite |
| recipient_email | str | INDEX | Destination email |
| payload | JSON | | Email template parameters |
| idempotency_key | str | UNIQUE, INDEX | Deduplication key |
| provider_message_id | str | NULLABLE | Brevo message ID |
| status | str | INDEX, DEFAULT "queued" | queued, sent, failed |
| attempts | int | DEFAULT 0 | Retry count |
| last_error | str | NULLABLE | Error message |
| sent_at | datetime | NULLABLE | Send timestamp |
| is_deleted | bool | DEFAULT false | Soft delete |
| created_at | datetime | | |
| updated_at | datetime | | |

#### feature_flag

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | **Tenant isolation** |
| key | str | UNIQUE, INDEX | Feature flag name |
| enabled | bool | DEFAULT false | Enable/disable state |
| is_deleted | bool | DEFAULT false | Soft delete |
| created_at | datetime | | |
| updated_at | datetime | | |

---

## 4. API Endpoints

### 4.1 Authentication (`/api/v1/auth`)

| Method | Endpoint | Rate Limit | Auth | Description |
|--------|----------|------------|------|-------------|
| POST | /login | 10/min | No | User login |
| POST | /register | 5/min | No | New user registration |
| POST | /refresh | 20/min | No | Refresh access token |
| POST | /reset-password | 5/min | No | Request password reset |
| POST | /reset-password/confirm | None | No | Confirm password change |
| POST | /verify-email | None | No | Verify email address |
| POST | /logout-all | None | Yes | Revoke all sessions |

**Request/Response Contracts:**

```python
# POST /login
LoginRequest:
  - email: EmailStr (validated)
  - password: str (min_length=8)

Token:
  - access_token: str
  - refresh_token: str
  - token_type: str = "bearer"

# POST /register (extends LoginRequest)
RegisterRequest:
  - email: EmailStr
  - password: str (min_length=8)
  - full_name: str | null
  - organization_name: str | null

# POST /refresh
RefreshRequest:
  - refresh_token: str

# POST /reset-password
ResetPasswordRequest:
  - email: EmailStr

# POST /reset-password/confirm
ConfirmResetPasswordRequest:
  - token: str
  - new_password: str (min_length=8)

# POST /verify-email
VerifyEmailRequest:
  - token: str
```

**Token Structure:**

```python
# Access Token
{
  "sub": "user-uuid",
  "type": "access",
  "exp": "2026-03-31T12:00:00Z",
  "tenant_id": "tenant-uuid",
  "rtv": 0  # refresh_token_version
}

# Refresh Token
{
  "sub": "user-uuid",
  "type": "refresh",
  "exp": "2026-04-07T12:00:00Z",
  "tenant_id": "tenant-uuid",
  "rtv": 0
}
```

### 4.2 Users (`/api/v1/users`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | / | Yes | List users (tenant-scoped) |
| GET | /me | Yes | Current user profile |

```python
# GET /api/v1/users
Query params:
  - limit: int (1-100, default 20)
  - offset: int (default 0)

Response: list[UserRead]
UserRead:
  - id: UUID
  - email: EmailStr
  - full_name: str | null

# GET /api/v1/users/me
Response: UserRead
```

### 4.3 Organizations (`/api/v1/organizations`)

| Method | Endpoint | Auth | Role Required | Description |
|--------|----------|------|---------------|-------------|
| GET | / | Yes | Any | List organizations |
| POST | / | Yes | owner, admin | Create organization |

```python
# GET /api/v1/organizations
Response: list[OrganizationRead]
OrganizationRead:
  - id: UUID
  - name: str

# POST /api/v1/organizations
OrganizationCreate:
  - name: str

Response: OrganizationRead
```

### 4.4 Billing (`/api/v1/billing`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | /plans | No | Available subscription plans |
| POST | /checkout | Yes | Create subscription |
| POST | /portal | Yes | Get customer portal URL |
| POST | /webhook | No | Asaas webhook receiver |
| GET | /subscription | Yes | Current subscription details |

```python
# GET /api/v1/billing/plans
Response: list[Plan]
Plan:
  - id: str (starter, growth, scale)
  - name: str
  - amount: float
  - billing_cycle: str

# POST /api/v1/billing/checkout
CheckoutRequest:
  - plan_id: str

Response: {"subscription_id": str, "status": str}

# POST /api/v1/billing/portal
PortalRequest:
  - return_url: str | null

Response: {"portal_url": str}

# POST /api/v1/billing/webhook
AsaasWebhookPayload:
  - event: str
  - id: str | null
  - payment: dict | null
  - subscription: dict | null

# GET /api/v1/billing/subscription
Response: SubscriptionRead
SubscriptionRead:
  - status: str
  - asaas_subscription_id: str | null
  - plan_id: str
  - value: float
  - next_due_date: date | null
```

**Available Plans:**

```python
PLANS = {
    "starter": {"id": "starter", "name": "Starter", "amount": 49.0, "billing_cycle": "MONTHLY"},
    "growth": {"id": "growth", "name": "Growth", "amount": 149.0, "billing_cycle": "MONTHLY"},
    "scale": {"id": "scale", "name": "Scale", "amount": 399.0, "billing_cycle": "MONTHLY"},
}
```

### 4.5 Health (`/api/v1/health`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | / | No | Service health check |

### 4.6 Core Feature (`/api/v1/core-feature`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | / | Yes | Feature flag status |

---

## 5. End-to-End Flows

### 5.1 User Registration Flow

```
1. User POST /api/v1/auth/register
   - Email, password, full_name, organization_name
   
2. Backend creates:
   - Organization (tenant_id = organization.id)
   - User (tenant_id = tenant_id, role = owner)
   - AuditLog entry
   
3. Celery task triggers:
   - send_transactional_email_task (welcome)
   
4. Response: Token (access + refresh)
```

### 5.2 Authentication Flow

```
1. User POST /api/v1/auth/login
   - Rate limited: 10 attempts/minute
   - In-memory brute-force protection (5 failures = 15 min block)
   
2. JWT created with:
   - sub: user.id
   - type: access/refresh
   - tenant_id: user.tenant_id
   - rtv: user.refresh_token_version
   
3. AuditLog: auth.login
4. last_login_at updated
```

### 5.3 Token Refresh Flow

```
1. POST /api/v1/auth/refresh
   - Submit refresh_token
   
2. Validate:
   - Token signature
   - Token type = "refresh"
   - rtv matches user.refresh_token_version
   
3. Issue new token pair
4. Old access tokens remain valid until expiration
```

### 5.4 Subscription Checkout Flow

```
1. POST /api/v1/billing/checkout
   - User authenticated + tenant validated
   
2. AsaasService.ensure_customer():
   - Check existing AsaasCustomer
   - Create new customer in Asaas if not exists
   
3. AsaasService.create_checkout():
   - Create subscription in Asaas
   - Returns subscription_id, status, next_due_date
   
4. Save/Update Subscription in database
5. AuditLog: billing.checkout
6. Return subscription details
```

### 5.5 Webhook Processing Flow

```
1. POST /api/v1/billing/webhook
   - Validate ASAAS_WEBHOOK_SECRET
   
2. Store AsaasWebhookEvent:
   - Save raw payload
   - processing_status = "pending"
   
3. AsaasService.sync_subscription_from_webhook():
   - Update subscription status
   - Update next_due_date
   - Set activated_at / canceled_at
   
4. Update webhook event:
   - processing_status = "processed" or "failed"
   - processed_at timestamp
   
5. AuditLog: billing.webhook_processed
```

### 5.6 Password Reset Flow

```
1. POST /api/v1/auth/reset-password
   - Submit email (rate limited: 5/min)
   
2. If user exists and active:
   - Generate reset_password_token (32 char)
   - Set reset_password_expires_at (1 hour)
   - Celery task: send reset email
   - AuditLog: auth.reset_password_requested
   
3. Always return: "If the account exists, reset instructions were generated"
   (Prevents email enumeration)

4. POST /api/v1/auth/reset-password/confirm
   - Validate token exists and not expired
   - Update hashed_password
   - Clear reset token fields
   - Increment refresh_token_version (invalidates old tokens)
```

### 5.7 Multi-Tenant Isolation Flow

```
1. Request includes header: X-Tenant-ID
   
2. TenantMiddleware extracts:
   - Validates UUID format
   - Sets request.state.tenant_id
   
3. get_current_tenant dependency:
   - Requires X-Tenant-ID header
   - Validates tenant matches current_user.tenant_id
   
4. All database queries:
   - Include tenant_id filter
   - Soft delete filter: is_deleted = false
```

---

## 6. Security Architecture

### 6.1 Authentication

- **JWT Algorithm:** HS256
- **Access Token Expiry:** 30 minutes
- **Refresh Token Expiry:** 7 days
- **Password Hashing:** bcrypt (via passlib)
- **Token Versioning:** refresh_token_version for revocation

### 6.2 Rate Limiting

- **Provider:** slowapi (Redis-backed)
- **Default:** 200/minute per IP
- **Specific endpoints:**
  - Login: 10/minute
  - Register: 5/minute
  - Refresh: 20/minute
  - Reset password: 5/minute

### 6.3 Security Headers

Implemented via SecurityHeadersMiddleware:

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
Content-Security-Policy: default-src 'self'; img-src 'self' data:; script-src 'self'; style-src 'self' 'unsafe-inline'
```

### 6.4 CORS Configuration

- **allow_credentials:** true
- **allow_methods:** GET, POST, PUT, DELETE, PATCH, OPTIONS
- **allow_headers:** Authorization, Content-Type, X-Tenant-ID

---

## 7. Configuration

### 7.1 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| DATABASE_URL | Yes | postgresql+asyncpg://... | PostgreSQL connection |
| REDIS_URL | Yes | redis://... | Redis connection |
| REDIS_PASSWORD | No | dev-redis-password | Redis auth |
| JWT_SECRET_KEY | Yes | dev-secret-key | **CHANGE IN PRODUCTION** |
| JWT_ALGORITHM | No | HS256 | JWT signing algorithm |
| ACCESS_TOKEN_EXPIRE_MINUTES | No | 30 | Access token TTL |
| REFRESH_TOKEN_EXPIRE_DAYS | No | 7 | Refresh token TTL |
| ASAAS_API_KEY | No | (empty) | Asaas production key |
| ASAAS_WEBHOOK_SECRET | No | (empty) | Webhook validation |
| ASAAS_ENVIRONMENT | No | sandbox | sandbox or production |
| BREVO_API_KEY | No | (empty) | Brevo API key |
| BREVO_SENDER_EMAIL | No | noreply@example.com | Email sender |
| BREVO_SENDER_NAME | No | SaaS Boilerplate | Sender display name |
| BREVO_TEMPLATE_WELCOME_ID | No | 0 | Welcome email template ID |
| BREVO_TEMPLATE_RESET_ID | No | 0 | Reset password template ID |
| BREVO_TEMPLATE_INVITE_ID | No | 0 | Invite template ID |
| CORS_ORIGINS | No | http://localhost:3000,... | Allowed origins |
| ALLOWED_HOSTS | No | localhost,127.0.0.1 | Host validation |
| PROJECT_NAME | No | SaaS Boilerplate | App name |
| API_V1_STR | No | /api/v1 | API prefix |
| DEBUG | No | true | Debug mode |
| SENTRY_DSN | No | (empty) | Sentry error tracking |

---

## 8. Integration Services

### 8.1 Asaas (Payment Gateway)

**Base URL:** 
- Sandbox: https://api.asaas.com/v3
- Production: https://api.asaas.com/v3

**Endpoints used:**
- POST /customers - Create customer
- POST /subscriptions - Create subscription
- POST /customerPortal/session - Customer portal URL

**Webhook events:** PAYMENT_RECEIVED, SUBSCRIPTION_CREATED, SUBSCRIPTION_UPDATED, SUBSCRIPTION_CANCELED

### 8.2 Brevo (Email Service)

**Base URL:** https://api.brevo.com/v3

**Endpoint:** POST /smtp/email (template send)

**Templates:**
- welcome - New user registration
- reset - Password reset
- invite - Organization invite

**Idempotency:** Keys prevent duplicate sends

---

## 9. Background Tasks (Celery)

### 9.1 Task: send_transactional_email_task

- **Queue:** celery
- **Broker:** Redis
- **Retry:** 5 attempts with exponential backoff
- **Templates:** welcome, reset, invite

### 9.2 Celery Beat (Scheduler)

- Not currently configured with periodic tasks
- Ready for future cron jobs (subscription reminders, etc.)

---

## 10. Development Status & Maturity Assessment

### 10.1 Functional Coverage

| Feature | Status | Notes |
|---------|--------|-------|
| User Registration | Complete | Basic registration with tenant creation |
| Login/Logout | Complete | JWT-based with refresh tokens |
| Password Reset | Complete | Token-based flow |
| Email Verification | Complete | Token-based flow |
| Multi-Tenant Isolation | Complete | Middleware + dependency injection |
| User Management | Complete | List users, get current user |
| Organization CRUD | Partial | List + create only |
| Subscription Plans | Complete | 3 tiers (starter/growth/scale) |
| Checkout Flow | Complete | Asaas integration |
| Customer Portal | Complete | Asaas portal URL |
| Webhook Handling | Complete | Event processing |
| Audit Logging | Partial | Most actions logged |
| Feature Flags | Basic | Simple key-value store |
| Email Templates | Complete | Brevo integration |

### 10.2 Security Maturity

| Aspect | Level | Notes |
|--------|-------|-------|
| Authentication | Good | JWT with refresh tokens |
| Password Storage | Good | bcrypt |
| Rate Limiting | Partial | Some endpoints unprotected |
| Token Revocation | Partial | Version-based, no blacklist |
| Tenant Isolation | Good | Middleware + DB filters |
| Input Validation | Good | Pydantic schemas |
| HTTPS/TLS | Infrastructure | Must be configured at reverse proxy |
| API Keys | Weak | Defaults provided in config |

### 10.3 Code Quality

| Aspect | Status |
|--------|--------|
| Type Hints | Good (Python) / Basic (TypeScript) |
| Linting | Configured (ruff, eslint) |
| Testing | Basic pytest suite + Playwright e2e |
| Error Handling | Partial |
| Documentation | Good (internal docs + docstrings) |
| CI/CD | Configured (GitHub Actions) |

### 10.4 Known Issues (from Security Report)

**Critical (4):**
1. JWT secret has default value
2. FAILED_LOGINS uses in-memory dict (not distributed-safe)
3. Cache decorator not implemented
4. API keys are optional (no production validation)

**High (5):**
1. Tenant middleware silently accepts missing headers
2. Missing rate limits on sensitive endpoints
3. Webhook doesn't validate event types
4. Rate limiter doesn't handle X-Forwarded-For

**Medium (6):**
1. Token revocation doesn't invalidate active sessions
2. Email verification not enforced at login
3. Audit logs missing on password reset confirm
4. No duplicate organization name validation
5. CORS with credentials + dynamic origins

---

## 11. Deployment

### 11.1 Docker Compose (Production)

Services:
- postgres:16
- redis:7
- backend (FastAPI)
- celery-worker
- celery-beat
- frontend (nginx)

### 11.2 Development

```bash
docker-compose -f docker-compose.dev.yml up
```

### 11.3 External Platforms

- **Render.com:** render.yaml configured
- **GitHub Actions:** CI/CD pipelines for backend/frontend

---

## 12. Recommendations for Production

1. **Secrets:** Remove all default values from config.py
2. **Rate Limiting:** Move FAILED_LOGINS to Redis
3. **Token Revocation:** Implement blacklist in Redis
4. **Tenant Validation:** Make X-Tenant-ID mandatory
5. **Email Verification:** Enforce at login time
6. **Audit Logs:** Add to password reset confirm
7. **Input Validation:** Validate organization names for uniqueness
8. **CORS:** Use exact origin matching in production
9. **HTTPS:** Configure TLS at load balancer/reverse proxy
10. **Monitoring:** Enable Sentry error tracking

---

## 13. File Descriptions

### Backend Core Files

- **main.py:** FastAPI app initialization, middleware registration, startup events
- **config.py:** Pydantic settings class, environment variable management
- **database.py:** SQLModel async engine, session factory, table initialization
- **security.py:** JWT creation/validation, password hashing utilities
- **tenant.py:** Middleware extracting X-Tenant-ID header
- **cache.py:** Redis client (stub - not functional)
- **limiter.py:** slowapi rate limiter configuration
- **security_headers.py:** CSP and security header middleware

### Backend Models

- **base.py:** BaseModel with tenant_id, timestamps, soft delete
- **user.py:** User entity with auth fields
- **organization.py:** Organization (tenant) entity
- **subscription.py:** Subscription with Asaas integration fields
- **asaas_customer.py:** Asaas customer mapping
- **asaas_webhook_event.py:** Webhook event logging
- **audit_log.py:** Audit trail storage
- **email_delivery:** Email tracking with idempotency
- **feature_flag.py:** Feature toggle storage

### Backend Services

- **asaas_service.py:** Asaas API client, customer/subscription management
- **email_service.py:** Brevo API client, template sending
- **audit_service.py:** Audit log writer
- **feature_flag_service.py:** Feature flag reader

### Backend Endpoints

- **auth.py:** Login, register, refresh, password reset, logout
- **users.py:** List users, current user
- **organizations.py:** List/create organizations
- **billing.py:** Plans, checkout, portal, webhook, subscription
- **health.py:** Health check
- **core_feature.py:** Feature flag demo

### Frontend

- **types/index.ts:** TypeScript interfaces
- **lib/api.ts:** Axios instance with auth headers
- **hooks/useAuth.tsx:** Authentication state management
- **hooks/useTenant.tsx:** Tenant context provider
- **hooks/useApi.tsx:** API call wrapper with error handling
- **store/authStore.ts:** Zustand auth state
- **store/tenantStore.ts:** Zustand tenant state

---

*This documentation provides a complete overview of the SaaS Boilerplate architecture. For detailed API specifications, see the FastAPI auto-generated docs at /docs after starting the backend.*