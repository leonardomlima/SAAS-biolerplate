# TestResult_002 - Análise de Falhas de Testes

## Data: 2026-04-01

## Resumo Executivo

Este relatório documenta a análise aprofundada do lifecycle das fixtures de teste, as causas raiz dos 9 testes falhando e as tentativas de correção implementadas no `conftest.py`.

---

## 1. Análise do Lifecycle das Fixtures

### 1.1 Arquitetura Atual do `conftest.py`

```
┌─────────────────────────────────────────────────────────────────┐
│                     FLUXO DE FIXTURES                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  setup_database (session)                                        │
│  ├── Importa app.core.database.engine                           │
│  ├── Cria tabelas via SQLModel.metadata.create_all             │
│  └── ⚠️ Usa asyncio.run() - cria event loop separado          │
│                                                                 │
│  clean_and_reset (function, autouse=True)                      │
│  ├── TRUNCATE via asyncpg.connect()                            │
│  ├── limiter._storage.reset()                                  │
│  ├── yield                                                     │
│  └── TRUNCATE no teardown                                      │
│                                                                 │
│  unique_email, unique_org (function)                            │
│  └── Gera valores únicos via uuid                              │
│                                                                 │
│  client (async function)                                        │
│  ├── dependency_overrides[get_session]                         │
│  ├── ASGITransport(app=app)                                    │
│  └── AsyncClient                                               │
│                                                                 │
│  auth_headers (async function)                                  │
│  ├── client + unique_email + unique_org                       │
│  └── Registra usuário e faz login                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Mapeamento de Recursos

| Recurso | Origem | Escopo | Problema Identificado |
|---------|--------|--------|----------------------|
| `engine` | `app/core/database.py:9` | Módulo (singleton) | Múltiplos event loops causam "attached to different loop" |
| `SessionLocal` | `app/core/database.py:10` | Módulo (singleton) | Mesmo problema do engine |
| `AsyncSession` | SQLModel | Session local | Requer mesmo event loop do engine |
| `limiter` | `app/core/limiter.py:4` | Módulo (singleton) | Estado global compartilhado entre testes |
| `app` | `app/main.py:19` | Módulo (singleton) | Não é recarregado entre testes |

### 1.3 Problema Principal: Múltiplos Event Loops

O fixture `setup_database` usa `asyncio.run(init())` que cria um NOVO event loop:
```python
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    asyncio.run(init())  # 🔴 CRIA NOVO EVENT LOOP
```

Este event loop é descartado após a função, mas o engine SQLAlchemy fica vinculado a ele.

---

## 2. Reprodução dos 9 Falhos no Container Linux

### 2.1 Stack Traces Coletados

#### Teste 1: `test_register_and_login_flow`
```
assert 409 == 200
- Response: {"detail": "Email already registered"}
- Causa: Usuário "owner@example.com" persiste no banco
```

#### Teste 2: `test_e2e_register_login_refresh_me`
```
RuntimeError: Task attached to a different loop
sqlalchemy.exc.InterfaceError: cannot perform operation: another operation is in progress
```

#### Teste 3: `test_e2e_organization_create_and_list`
```
sqlalchemy.exc.InterfaceError: cannot perform operation: another operation is in progress
```

#### Teste 4: `test_e2e_authenticated_billing_checkout`
```
sqlalchemy.exc.InterfaceError: cannot perform operation: another operation is in progress
```

#### Teste 5: `test_e2e_authenticated_billing_subscription`
```
sqlalchemy.exc.InterfaceError: cannot perform operation: another operation is in progress
```

#### Teste 6: `test_e2e_organization_isolation_between_users`
```
KeyError: 'access_token'
- Response: 409 Conflict - "Email already registered"
```

#### Teste 7: `test_e2e_full_user_journey`
```
KeyError: 'access_token'
- Response: 409 Conflict - "Email already registered"  
```

#### Teste 8: `test_create_and_list_orgs`
```
assert 429 == 200
- 429 = Rate limit exceeded
```

#### Teste 9: `test_users_me`
```
assert 429 == 200
- 429 = Rate limit exceeded
```

### 2.2 Verificação do Estado do Banco

```bash
# Antes de rodar testes (depois de TRUNCATE manual):
User count: 0

# Depois de rodar 1 teste:
User count: 1  # Usuário persiste!

# O fixture clean_and_reset NÃO está funcionando
```

### 2.3 Análise: O Fixture `clean_and_reset` Não Executa

Investigação detalhada:
1. O pytest executa `clean_and_reset` antes de cada teste
2. O cleanup DEVERIA executar asyncpg.connect() no event loop correto
3. MAS... verificação mostra que usuários persistem

**Causa Raiz Identificada:**
O pytest-asyncio está criando um event loop NOVO para cada teste (devido a `asyncio_default_fixture_loop_scope = "function"`), mas o cleanup usa `asyncpg.connect()` que também cria uma conexão nova. A race condition entre o cleanup e o teste causa o problema.

---

## 3. Tentativas de Correção Implementadas

### 3.1 Tentativa 1: Cleanup Síncrono com asyncio.run()
```python
# PROBLEMA: Cria event loop separado - mesmo problema do engine
def _cleanup_db():
    asyncio.run(_cleanup_db_async())  # ❌ NÃO FUNCIONA
```

### 3.2 Tentativa 2: Cleanup Async com pytest_asyncio.fixture
```python
# PROBLEMA: mesmo assim não executa antes do primeiro teste
@pytest_asyncio.fixture(autouse=True)
async def clean_and_reset():
    await cleanup()
```

### 3.3 Tentativa 3: Usar dependency_overrides ao invés de reload
```python
# Melhora: Não usa mais importlib.reload()
# PROBLEMA: O cleanup asyncpg ainda não funciona corretamente
app.dependency_overrides[get_session] = override_get_session
```

### 3.4 Tentativa 4: Adicionar teardown cleanup
```python
# Teardown também faz cleanup
yield
# cleanup again
await cleanup()  # ❌ NÃO FUNCIONA
```

### 3.5 Tentativa 5: Remover rate limiting para testes
```python
# Não resolução: ainda persiste o problema de banco sujo
@pytest.fixture(autouse=True)
def reset_limiter():
    limiter._storage.reset()
```

---

## 4. Correções de Arquivos de Teste

### 4.1 test_auth_rate_limit.py
**Problema:** Criava seu próprio AsyncClient, não usava fixture `client`
**Correção:** Agora usa fixture `client` que tem rate limit resetado

```diff
- async def test_login_rate_limit_returns_client_error_for_invalid_payload():
-     from app.main import app
-     async with httpx.AsyncClient(
-         transport=ASGITransport(app=app),
-         base_url="http://test",
-         headers={"host": "testserver"},
-     ) as client:
-         response = await client.post(...)
+ async def test_login_rate_limit_returns_client_error_for_invalid_payload(client):
+     response = await client.post(...)
```

### 4.2 test_security_headers.py
**Problema:** Mesmo que acima
**Correção:** Agora usa fixture `client`

---

## 5. Estado Atual - 9 Falhas Remanescentes

| # | Teste | Status | Causa Raiz |
|---|-------|--------|------------|
| 1 | test_register_and_login_flow | FAILED (409) | Banco não limpo antes do teste |
| 2 | test_e2e_register_login_refresh_me | FAILED (Event Loop) | Conexão asyncpg em loop errado |
| 3 | test_e2e_organization_create_and_list | FAILED (Event Loop) | Mesmo problema |
| 4 | test_e2e_authenticated_billing_checkout | FAILED (Event Loop) | Mesmo problema |
| 5 | test_e2e_authenticated_billing_subscription | FAILED (Event Loop) | Mesmo problema |
| 6 | test_e2e_organization_isolation_between_users | FAILED (409) | Banco não limpo |
| 7 | test_e2e_full_user_journey | FAILED (409) | Banco não limpo |
| 8 | test_create_and_list_orgs | FAILED (429) | Rate limit não resetado |
| 9 | test_users_me | FAILED (429) | Rate limit não resetado |

---

## 6. Causa Raiz Técnica Verificável

### 6.1 O Problema Fundamental

O SQLAlchemy async engine é vinculado a um event loop específico:
```python
# app/core/database.py
engine = create_async_engine(settings.DATABASE_URL, echo=False)
```

Quando `setup_database` fixture executa:
```python
asyncio.run(init())  # cria event loop A
```

O engine é configurado no event loop A.

Quando os testes executam, cada um pode ter um event loop diferente (devido ao pytest-asyncio com `function` scope).

Quando tentamos cleanup com asyncpg:
```python
conn = await asyncpg.connect(db_url)  # pode usar loop diferente
await conn.execute('TRUNCATE...')      # compete com loop do engine
```

### 6.2 Por Que o Cleanup Não Funciona

1. **Race condition:** O teste pode executar antes do cleanup completar
2. **Event loop mismatch:** A conexão asyncpg pode usar loop diferente do engine
3. **Session scope:** O `setup_database` usa `asyncio.run()` que é síncrono e cria loop separado

---

## 7. Próximos Passos Recomendados

### Solução Robusta Proposta:

1. **Remover setup_database** - não criar tabelas em fixture de sessão
2. **Usar engine bypassado** - não usar o engine do módulo app
3. **Criar engine de teste dedicado** em cada teste
4. **Usar pytest-asyncio com mode=strict** - controlar event loops explicitamente
5. **Testar com sqlite in-memory** - para isolamento total

### Alternativa Imediata (Workaround):

Adicionar retry/hardcoded cleanup antes de rodar testes:
```bash
python -c "cleanup asyncpg" && pytest
```

---

## 8. Arquivos Modificados

- `backend/tests/conftest.py` - Múltiplas tentativas de correção
- `backend/tests/test_auth_rate_limit.py` - Usar fixture client
- `backend/tests/test_security_headers.py` - Usar fixture client
- `backend/pyproject.toml` - Adicionar asyncio_default_fixture_loop_scope

---

## 9. Resultado Final

**ANTES:** 4 falhas (conforme z_TestResult_001.md)
**DEPOIS:** 9 falhas (após tentativas de correção)

O problema de event loop é mais profundo que o esperado. A arquitetura atual com engine singleton não é compatível com testes isolados sem uma refatoração significativa.

---

## 10. Diff: Estado Original vs Atual

### 10.1 conftest.py - Estado Original (4 falhas)
```python
# key parts
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    import asyncio
    from sqlalchemy.ext.asyncio import create_async_engine
    
    _cleanup_db()
    atexit.register(_cleanup_db)
    
    db_url = os.environ.get("DATABASE_URL", ...)
    engine = create_async_engine(db_url, echo=False)
    from app.core.database import Base
    
    async def init():
        async with engine.begin() as conn:
            await conn.run_sync(Base.create_all)
    
    asyncio.run(init())  # 🔴 PROBLEMA: cria event loop separado
    
    yield
    
    asyncio.run(engine.dispose())

@pytest_asyncio.fixture
async def client():
    from importlib import reload
    import app.core.database as db_module
    import app.main
    
    reload(db_module)
    app_instance = reload(app.main).app  # 🔴 Usava reload!
    
    await asyncio.sleep(0.05)
    
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app_instance),
        ...
    ) as ac:
        yield ac
```

### 10.2 conftest.py - Estado Atual (9 falhas)
```python
# key changes
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    from app.core.database import engine
    from sqlmodel import SQLModel
    
    async def init():
        from app import models
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
    
    asyncio.run(init())  # Still uses separate loop
    
    yield

@pytest_asyncio.fixture(autouse=True)
async def clean_and_reset():
    import asyncpg
    
    await asyncio.sleep(0.05)
    
    conn = await asyncpg.connect(_get_sync_db_url())
    try:
        await conn.execute('TRUNCATE...')  # Cleanup async
    finally:
        await conn.close()
    
    from app.core.limiter import limiter
    limiter._storage.reset()
    
    yield

@pytest_asyncio.fixture
async def client():
    from app.core.database import get_session, SessionLocal
    from app.main import app
    
    async def override_get_session():
        async with SessionLocal() as session:
            yield session
    
    app.dependency_overrides[get_session] = override_get_session
    
    try:
        async with httpx.AsyncClient(
            transport=ASGITransport(app=app),
            ...
        ) as ac:
            yield ac
    finally:
        app.dependency_overrides.clear()
```

### 10.3 test_auth_rate_limit.py - Mudanças

**ANTES:**
```python
async def test_login_rate_limit_returns_client_error_for_invalid_payload():
    from app.main import app
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app),
        ...
    ) as client:
        response = await client.post(...)
```

**DEPOIS:**
```python
async def test_login_rate_limit_returns_client_error_for_invalid_payload(client):
    response = await client.post(...)
```

### 10.4 test_security_headers.py - Mudanças

**ANTES:**
```python
async def test_security_headers_present():
    from app.main import app
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app),
        ...
    ) as client:
        response = await client.get(...)
```

**DEPOIS:**
```python
async def test_security_headers_present(client):
    response = await client.get(...)
```

### 10.5 pyproject.toml - Mudanças

**ANTES:**
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

**DEPOIS:**
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
filterwarnings = [
    "ignore::DeprecationWarning",
]
```

---

## 11. Conclusão

O problema fundamental é que:

1. **O engine SQLAlchemy é criado no nível do módulo** (`app/core/database.py:9`)
2. **O `setup_database` fixture usa `asyncio.run()`** que cria um event loop separado
3. **Os testes usam event loops diferentes** (um por teste com `function` scope)
4. **O cleanup asyncpg compete com o loop do engine** causando "another operation in progress"

**Solução recomendada:** Refatorar `app/core/database.py` para usar injeção de dependência em vez de variáveis de módulo, permitindo que testes substituam o engine.

---

*Relatório gerado em 2026-04-01*
*Ambiente: Docker container Linux (postgres:5432, Python 3.12)*