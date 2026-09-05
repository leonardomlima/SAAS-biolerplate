# Security & Logic Analysis Report

**Data:** 31/03/2026  
**Projeto:** SaaS Boilerplate  
**Versão:** 0.1.0

---

## Sumário Executivo

Esta análise identificou **17 issues**classificados em 4 níveis de severidade:
- **CRÍTICO:** 4 issues
- **ALTO:** 5 issues  
- **MÉDIO:** 6 issues
- **BAIXO:** 2 issues

As principais vulnerabilidades envolvem autenticação, proteção de dados, isolamento multi-tenant e configuração de segurança.

---

## 1. Issues Críticos

### 1.1 Segredo JWT com Valor Hardcoded Padrão

**Localização:** `backend/app/core/config.py:9`

```python
JWT_SECRET_KEY: str = "dev-secret-key"
```

**Problema:** A chave JWT possui um valor padrão inseguro que será usado se a variável de ambiente não estiver configurada. Em produção, isso pode levar à comprometimento total de tokens.

**Risco:** Comprometimento de autenticação, escalação de privilégios.

**Correção:**
```python
JWT_SECRET_KEY: str = ""  # Não fornecer default - falhar se não configurado
```

---

### 1.2 Estado Global Mutável para Rate Limiting de Login

**Localização:** `backend/app/api/v1/endpoints/auth.py:28`

```python
FAILED_LOGINS: dict[str, tuple[int, datetime]] = {}
```

**Problema:** Armazenamento em memória não persiste entre reinícios do worker, não funciona em ambiente distribuído (múltiplos containers) e consome memória não-limited. Não há cleanup de entradas antigas.

**Risco:** Ataques DDoS via memória, rate limit bypass em ambiente distribuído.

**Correção:** Utilizar Redis com TTL para rate limiting:
```python
# Usar Redis com ключ "failed_login:{email}" e TTL de 15 minutos
```

---

### 1.3 Decorator de Cache Não Implementado

**Localização:** `backend/app/core/cache.py:15-21`

```python
def cached(prefix: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)  # Sem cache!
        return wrapper
    return decorator
```

**Problema:** O decorator `cached` não implementa nenhuma lógica de caching - apenas executa a função original.

**Risco:** Performance degradada, calls desnecessários ao banco/API externa.

**Correção:** Implementar cache Redis:
```python
async def wrapper(*args, **kwargs):
    key = f"{prefix}:{hash_args}"
    if cached := await redis_client.get(key):
        return json.loads(cached)
    result = await func(*args, **kwargs)
    await redis_client.setex(key, 300, json.dumps(result))
    return result
```

---

### 1.4 Falta de Validação de_API Key em Ambiente de Produção

**Localização:** `backend/app/core/config.py:13-14`

```python
ASAAS_API_KEY: str = ""
BREVO_API_KEY: str = ""
```

**Problema:** APIs podem operar com chaves vazias em produção sem fallback seguro, resultando em exceptions não tratadas ou comportamento inesperado.

**Risco:** indisponibilidade de funcionalidades críticas (pagamentos, emails).

**Correção:** Adicionar validação na inicialização:
```python
@validator("ASAAS_API_KEY")
def validate_asaas_key(cls, v):
    if not v and not settings.DEBUG:
        raise ValueError("ASAAS_API_KEY required in production")
    return v
```

---

## 2. Issues de Alto

### 2.1 Middleware Tenant Silentemente Aceita Requisições Sem Header

**Localização:** `backend/app/core/tenant.py:8-17`

```python
if tenant_id:
    try:
        request.state.tenant_id = str(UUID(tenant_id))
    except ValueError:
        request.state.tenant_id = None
else:
    request.state.tenant_id = None  # Silencioso!
```

**Problema:** Requisições sem `X-Tenant-ID` passam pelo middleware sem erro, permitindo que endpoints dependentes de tenant sejam chamados sem validação adequada.

**Risco:** vazamento de dados cross-tenant, isolamento comprometido.

**Correção:** No endpoint dependente, verificar explicitamente:
```python
if not tenant_id:
    raise HTTPException(status_code=400, detail="X-Tenant-ID required")
```

---

### 2.2 Sem Rate Limiting em Endpoint de Confirmação de Senha

**Localização:** `backend/app/api/v1/endpoints/auth.py:173`

```python
@router.post("/reset-password/confirm", response_model=MessageResponse)
async def confirm_reset_password(...):  # Sem @limiter.limit!
```

**Problema:** Endpoint de alta sensibilidade não possui rate limiting, permitindo força bruta no token de reset.

**Risco:** Comprometimento de contas via brute force.

**Correção:**
```python
@router.post("/reset-password/confirm", response_model=MessageResponse)
@limiter.limit("5/minute")
async def confirm_reset_password(...):
```

---

### 2.3 Sem Rate Limiting em Endpoint de Verificação de Email

**Localização:** `backend/app/api/v1/endpoints/auth.py:191`

```python
@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(...):  # Sem rate limiting!
```

**Problema:** Permite enumeração de tokens de verificação de email.

**Risco:** Enumeração de usuários, força bruta em tokens.

**Correção:** Adicionar rate limiting:
```python
@router.post("/verify-email")
@limiter.limit("10/minute")
async def verify_email(...):
```

---

### 2.4 Validação Ausente no Webhook Asaas

**Localização:** `backend/app/api/v1/endpoints/billing.py:122-173`

```python
@router.post("/webhook")
async def webhook(payload: AsaasWebhookPayload, ...):
    if settings.ASAAS_WEBHOOK_SECRET and asaas_access_token != settings.ASAAS_WEBHOOK_SECRET:
        raise HTTPException(status_code=401, ...)
    # Processa qualquer evento sem validar tipo
```

**Problema:** Webhook processa qualquer evento sem validar o tipo (PAYMENT, SUBSCRIPTION, etc), permitindo processamento de eventos inesperados.

**Risco:** Processamento de eventos maliciosos, inconsistência de dados.

**Correção:**
```python
ALLOWED_EVENTS = {"PAYMENT_RECEIVED", "SUBSCRIPTION_CREATED", "SUBSCRIPTION_UPDATED", "SUBSCRIPTION_CANCELED"}
if payload.event not in ALLOWED_EVENTS:
    return {"ok": True, "skipped": True}  # Ignorar eventos não esperados
```

---

### 2.5 Limiter Usando IP Remoto Sem Suporte a Proxy

**Localização:** `backend/app/core/limiter.py:1-4`

```python
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])
```

**Problema:** Em ambiente containerizado, todos os requests parecem virir do mesmo IP (docker network), não permitindo rate limiting por cliente real.

**Risco:** Rate limiting ineficaz em produção.

**Correção:**
```python
def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    return forwarded.split(",")[0].strip() if forwarded else request.client.host

limiter = Limiter(key_func=get_client_ip, default_limits=["200/minute"])
```

---

## 3. Issues de Médio

### 3.1 Refresh Token Não Invalida Access Tokens Ativos

**Localização:** `backend/app/api/v1/endpoints/auth.py:185`

```python
user.refresh_token_version += 1
```

**Problema:** Apenas incrementa versão do refresh token, mas não invalida tokens de acesso já emitidos. Usuários com tokens ativos permanecem logados até expiração natural.

**Risco:** Não permite logout forçado completo de todas as sessões.

**Correção:** Implementar blacklist de tokens no Redis:
```python
# Após incremento de rtv, adicionar token antigo à blacklist
await redis_client.setex(f"blacklist:{token}", 1800, "1")  # TTL = 30 min
```

---

### 3.2 Reset de Senha Não Invalida Sessões Ativas

**Localização:** `backend/app/api/v1/endpoints/auth.py:182-188`

```python
user.hashed_password = get_password_hash(payload.new_password)
user.refresh_token_version += 1
```

**Problema:** Permite que sessões ativas continuem usando tokens antigos até expiração. Usuário comprometido pode manter acesso mesmo após mudança de senha.

**Risco:** Persistência de acesso após comprometimento de senha.

**Correção:** Same as 3.1 - implementar blacklist.

---

### 3.3 Sem Verificação de Email Antes do Login

**Localização:** `backend/app/api/v1/endpoints/auth.py:46-47`

```python
if not user.is_active:
    raise HTTPException(status_code=403, detail="User inactive")
# Mas não verifica email_verified!
```

**Problema:** Usuários podem fazer login mesmo sem verificar email, dependendo apenas de `is_active`.

**Risco:** Acesso de usuários não confirmados.

**Correção:**
```python
if not user.email_verified:
    raise HTTPException(status_code=403, detail="Email not verified")
```

---

### 3.4 Missing Audit Log em Operações Sensíveis

**Localização:** `backend/app/api/v1/endpoints/auth.py:173-188`

```python
# Reset password confirm - sem audit log!
async def confirm_reset_password(...):
    user.hashed_password = get_password_hash(...)
    await session.commit()
    return MessageResponse(message="Password updated")  # Sem audit!
```

**Problema:** Operação crítica de alteração de senha não é registrada em audit log.

**Risco:** Sem rastreabilidade de mudanças de senha, investigação comprometida.

**Correção:**
```python
await write_audit_log(session, tenant_id=user.tenant_id, actor_user_id=user.id,
    action="auth.password_reset_confirmed", entity_type="user", entity_id=str(user.id))
```

---

### 3.5 Duplicate Organization Name Possível

**Localização:** `backend/app/api/v1/endpoints/organizations.py:29-42`

```python
organization = Organization(id=uuid4(), tenant_id=current_user.tenant_id, name=payload.name)
session.add(organization)
```

**Problema:** Não há validação de nomes duplicados dentro do mesmo tenant.

**Risco:** Dados inconsistentes, confusão de organizações.

**Correção:**
```python
existing = (await session.exec(select(Organization).where(
    Organization.tenant_id == current_user.tenant_id,
    Organization.name == payload.name,
    Organization.is_deleted.is_(False)
))).first()
if existing:
    raise HTTPException(status_code=409, detail="Organization already exists")
```

---

### 3.6 CORS Permite Credenciais com Origins Dinâmicas

**Localização:** `backend/app/main.py:42-48`

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[...],  # Origins configuráveis
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Tenant-ID"],
)
```

**Problema:** `allow_credentials=True` com origins dinâmicas do ambiente pode gerar vulnerabilidade CORS se ORIGINS incluir origem controlada por attacker.

**Risco:** Cross-site data theft.

**Correção:** Em produção, validar origins contra lista branca específica:
```python
origins = [o for o in allowed_origins if o.startswith("https://")]
# Ou usar exact match em vez de wildcard
```

---

## 4. Issues de Baixo

### 4.1 CSP Restritiva Para Resources Dinâmicos

**Localização:** `backend/app/core/security_headers.py:11`

```python
response.headers["Content-Security-Policy"] = "default-src 'self'; img-src 'self' data:; script-src 'self'; style-src 'self' 'unsafe-inline'"
```

**Problema:** Não permite loading de assets externos (fonts, CDNs, imagens de URLs externas).

**Risco:** Breaking de funcionalidades que dependem de resources externos.

**Correção:** Tornar configurável:
```python
response.headers["Content-Security-Policy"] = settings.CSP_POLICY  # "default-src 'self'; ..."
```

---

### 4.2 Dependência Cicl Implícita (Database Import in Tasks)

**Localização:** `backend/app/background/tasks.py:16`

```python
async def _run_email(template: str, kwargs: dict) -> None:
    from app.core.database import SessionLocal  # Import tardio!
```

**Problema:** Import dentro de função para evitar ciclagem, mas indica arquitetura que pode causar problemas em testes.

**Risco:** Dificuldade em testes, dependencies não explícitas.

**Correção:** Refatorar para injeção de dependência ou inicialização lazy no módulo.

---

## 5. Recomendações por Prioridade

| # | Severidade | Issue | Correção Prioritária |
|---|------------|-------|---------------------|
| 1 | CRÍTICO | JWT secret hardcoded | Remover default, fail fast |
| 2 | CRÍTICO | FAILED_LOGINS em memória | Migrar para Redis |
| 3 | CRÍTICO | Cache não implementado | Implementar ou remover decorator |
| 4 | CRÍTICO | API keys opcionais | Validação em startup |
| 5 | ALTO | Tenant header optional | Validação explícita em endpoints |
| 6 | ALTO | Rate limiting ausente | Adicionar em /reset-password/confirm e /verify-email |
| 7 | ALTO | Webhook sem validação de tipo | Whitelist de eventos |
| 8 | ALTO | Limiter sem suporte proxy | Usar X-Forwarded-For |
| 9 | MÉDIO | Token revocation incompleta | Blacklist no Redis |
| 10 | MÉDIO | Email verification bypass | Verificar email_verified |
| 11 | MÉDIO | Audit log ausente | Adicionar em password reset |
| 12 | MÉTIO | Duplicate org names | Validação uniqueness |
| 13 | MÉDIO | CORS credentials | Exact match origins |

---

## 6. Conclusão

O projeto apresenta uma arquitetura sólida de multi-tenancy, mas possui gaps críticos de segurança que devem ser endereçados antes de produção:

1. **Infraestrutura:** Secrets em defaults, cache não implementado
2. **Autenticação:** State global, rate limiting incompleto, token revocation parcial
3. **Isolamento:** Tenant header opcional, validação insuficiente
4. **Auditoria:** Logs ausentes em operações críticas

A correção dos items de severidade CRÍTICO e ALTO é mandatória antes do deploy.