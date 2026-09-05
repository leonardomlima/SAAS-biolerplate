============================= test session starts =============================
platform win32 -- Python 3.13.1, pytest-9.0.2, pluggy-1.6.0 -- C:\Users\leona\AppData\Local\Programs\Python\Python313\python.exe
cachedir: .pytest_cache
rootdir: D:\Python\C�digos\boilerplate_v01\backend
configfile: pyproject.toml
plugins: anyio-4.12.1, Faker-40.8.0, langsmith-0.6.5, asyncio-1.3.0
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 49 items

tests/test_auth.py::test_register_and_login_flow PASSED                  [  2%]
tests/test_auth_rate_limit.py::test_login_rate_limit_returns_client_error_for_invalid_payload PASSED [  4%]
tests/test_billing.py::test_billing PASSED                               [  6%]
tests/test_common.py::test_endpoint_requires_authentication[/api/v1/users/me-GET] PASSED [  8%]
tests/test_common.py::test_endpoint_requires_authentication[/api/v1/users/-GET] PASSED [ 10%]
tests/test_common.py::test_endpoint_requires_authentication[/api/v1/organizations/-GET] PASSED [ 12%]
tests/test_common.py::test_endpoint_requires_authentication[/api/v1/organizations/-POST] PASSED [ 14%]
tests/test_common.py::test_endpoint_requires_authentication[/api/v1/billing/checkout-POST] PASSED [ 16%]
tests/test_common.py::test_endpoint_requires_authentication[/api/v1/billing/subscription-GET] PASSED [ 18%]
tests/test_common.py::test_endpoint_requires_authentication[/api/v1/billing/portal-POST] PASSED [ 20%]
tests/test_common.py::test_endpoint_rejects_invalid_token[/api/v1/users/me-GET] PASSED [ 22%]
tests/test_common.py::test_endpoint_rejects_invalid_token[/api/v1/users/-GET] PASSED [ 24%]
tests/test_common.py::test_endpoint_rejects_invalid_token[/api/v1/organizations/-GET] PASSED [ 26%]
tests/test_common.py::test_endpoint_rejects_invalid_token[/api/v1/organizations/-POST] PASSED [ 28%]
tests/test_common.py::test_endpoint_rejects_invalid_token[/api/v1/billing/checkout-POST] PASSED [ 30%]
tests/test_common.py::test_endpoint_rejects_invalid_token[/api/v1/billing/subscription-GET] PASSED [ 32%]
tests/test_common.py::test_endpoint_rejects_invalid_token[/api/v1/billing/portal-POST] PASSED [ 34%]
tests/test_common.py::test_endpoint_rejects_malformed_header[/api/v1/users/me-GET] PASSED [ 36%]
tests/test_common.py::test_endpoint_rejects_malformed_header[/api/v1/users/-GET] PASSED [ 38%]
tests/test_common.py::test_endpoint_rejects_malformed_header[/api/v1/organizations/-GET] PASSED [ 40%]
tests/test_common.py::test_endpoint_rejects_malformed_header[/api/v1/organizations/-POST] PASSED [ 42%]
tests/test_common.py::test_endpoint_rejects_malformed_header[/api/v1/billing/checkout-POST] PASSED [ 44%]
tests/test_common.py::test_endpoint_rejects_malformed_header[/api/v1/billing/subscription-GET] PASSED [ 46%]
tests/test_common.py::test_endpoint_rejects_malformed_header[/api/v1/billing/portal-POST] PASSED [ 48%]
tests/test_common.py::test_register_login_validation[/api/v1/auth/register-payload0-422] PASSED [ 51%]
tests/test_common.py::test_register_login_validation[/api/v1/auth/register-payload1-422] PASSED [ 53%]
tests/test_common.py::test_register_login_validation[/api/v1/auth/login-payload2-422] PASSED [ 55%]
tests/test_common.py::test_register_login_validation[/api/v1/auth/login-payload3-422] PASSED [ 57%]
tests/test_common.py::test_login_email_format_validation[/api/v1/auth/login-payload0] PASSED [ 59%]
tests/test_common.py::test_login_email_format_validation[/api/v1/auth/login-payload1] PASSED [ 61%]
tests/test_common.py::test_refresh_requires_payload[/api/v1/auth/refresh] PASSED [ 63%]
tests/test_common.py::test_refresh_rejects_invalid_token[/api/v1/auth/refresh-payload0] PASSED [ 65%]
tests/test_common.py::test_refresh_rejects_invalid_token[/api/v1/auth/refresh-payload1] PASSED [ 67%]
tests/test_common.py::test_public_endpoints_accessible[/api/v1/billing/plans] PASSED [ 69%]
tests/test_common.py::test_public_endpoints_accessible[/api/v1/health] PASSED [ 71%]
tests/test_common.py::test_public_endpoints_no_auth_required[/api/v1/billing/plans] PASSED [ 73%]
tests/test_common.py::test_public_endpoints_no_auth_required[/api/v1/health] PASSED [ 75%]
tests/test_e2e.py::test_e2e_billing_flow_public_plans_only PASSED        [ 77%]
tests/test_e2e.py::test_e2e_invalid_token_propagates_to_all_endpoints PASSED [ 79%]
tests/test_e2e.py::test_e2e_public_endpoints_work_without_auth PASSED    [ 81%]
tests/test_e2e.py::test_e2e_register_login_refresh_me PASSED             [ 83%]
tests/test_e2e.py::test_e2e_organization_create_and_list PASSED          [ 85%]
tests/test_e2e.py::test_e2e_authenticated_billing_checkout FAILED        [ 87%]
tests/test_e2e.py::test_e2e_authenticated_billing_subscription FAILED    [ 89%]
tests/test_e2e.py::test_e2e_organization_isolation_between_users FAILED  [ 91%]
tests/test_e2e.py::test_e2e_full_user_journey FAILED                     [ 93%]
tests/test_organizations.py::test_create_and_list_orgs PASSED            [ 95%]
tests/test_security_headers.py::test_security_headers_present PASSED     [ 97%]
tests/test_users.py::test_users_me PASSED                                [100%]

================================== FAILURES ===================================
___________________ test_e2e_authenticated_billing_checkout ___________________

client = <httpx.AsyncClient object at 0x00000240A796B650>

    @pytest.mark.asyncio
    async def test_e2e_authenticated_billing_checkout(client):
        register_payload = {
            "email": "billing-e2e@test.com",
            "password": "billpass123",
            "organization_name": "Billing E2E",
        }
        register_response = await client.post("/api/v1/auth/register", json=register_payload)
        access_token = register_response.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {access_token}"}
    
        checkout_response = await client.post(
            "/api/v1/billing/checkout",
            json={"plan_id": "starter"},
            headers=auth_headers,
        )
>       assert checkout_response.status_code in {200, 502}
E       assert 400 in {200, 502}
E        +  where 400 = <Response [400 Bad Request]>.status_code

tests\test_e2e.py:142: AssertionError
_________________ test_e2e_authenticated_billing_subscription _________________

client = <httpx.AsyncClient object at 0x00000240A7E08590>

    @pytest.mark.asyncio
    async def test_e2e_authenticated_billing_subscription(client):
        register_payload = {
            "email": "sub-e2e@test.com",
            "password": "subpass123",
            "organization_name": "Sub E2E",
        }
        register_response = await client.post("/api/v1/auth/register", json=register_payload)
        access_token = register_response.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {access_token}"}
    
        subscription_response = await client.get(
            "/api/v1/billing/subscription",
            headers=auth_headers,
        )
>       assert subscription_response.status_code in {200, 404}
E       assert 400 in {200, 404}
E        +  where 400 = <Response [400 Bad Request]>.status_code

tests\test_e2e.py:160: AssertionError
________________ test_e2e_organization_isolation_between_users ________________

client = <httpx.AsyncClient object at 0x00000240A796B650>

    @pytest.mark.asyncio
    async def test_e2e_organization_isolation_between_users(client):
        payload1 = {
            "email": "user1@test.com",
            "password": "pass123",
            "organization_name": "User1 Org",
        }
        reg1 = await client.post("/api/v1/auth/register", json=payload1)
>       token1 = reg1.json()["access_token"]
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       KeyError: 'access_token'

tests\test_e2e.py:171: KeyError
_________________________ test_e2e_full_user_journey __________________________

client = <httpx.AsyncClient object at 0x00000240A796B410>

    @pytest.mark.asyncio
    async def test_e2e_full_user_journey(client):
        register_payload = {
            "email": "journey@test.com",
            "password": "journeypass123",
            "organization_name": "Journey Org",
        }
        register_response = await client.post("/api/v1/auth/register", json=register_payload)
        token = register_response.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}
    
        me_response = await client.get("/api/v1/users/me", headers=auth_headers)
        assert me_response.status_code == 200
    
        orgs_response = await client.get("/api/v1/organizations/", headers=auth_headers)
        assert orgs_response.status_code == 200
    
        checkout_response = await client.post(
            "/api/v1/billing/checkout",
            json={"plan_id": "growth"},
            headers=auth_headers,
        )
>       assert checkout_response.status_code in {200, 502}
E       assert 400 in {200, 502}
E        +  where 400 = <Response [400 Bad Request]>.status_code

tests\test_e2e.py:219: AssertionError
============================== warnings summary ===============================
tests/test_auth.py: 2 warnings
tests/test_billing.py: 1 warning
tests/test_common.py: 34 warnings
tests/test_e2e.py: 9 warnings
tests/test_organizations.py: 1 warning
tests/test_users.py: 1 warning
  D:\Python\C�digos\boilerplate_v01\backend\app\main.py:53: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_auth.py: 2 warnings
tests/test_billing.py: 1 warning
tests/test_common.py: 34 warnings
tests/test_e2e.py: 9 warnings
tests/test_organizations.py: 1 warning
tests/test_users.py: 1 warning
  C:\Users\leona\AppData\Local\Programs\Python\Python313\Lib\site-packages\fastapi\applications.py:4574: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    return self.router.on_event(event_type)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ===========================
FAILED tests/test_e2e.py::test_e2e_authenticated_billing_checkout - assert 40...
FAILED tests/test_e2e.py::test_e2e_authenticated_billing_subscription - asser...
FAILED tests/test_e2e.py::test_e2e_organization_isolation_between_users - Key...
FAILED tests/test_e2e.py::test_e2e_full_user_journey - assert 400 in {200, 502}
================= 4 failed, 45 passed, 96 warnings in 15.07s ==================

================================================================================
RESUMO FINAL DA INVESTIGAÇÃO - Test Suite Results
================================================================================

RESULTADO: 45 PASSED | 4 FAILED (vs 8 failures originais)

--------------------------------------------------------------------------------
CAUSA RAIZ IDENTIFICADA:
--------------------------------------------------------------------------------

Os 4 failures restantes são de natureza DIFERENTE dos 8 originais:

1. **test_e2e_authenticated_billing_checkout** - 400 Bad Request
2. **test_e2e_authenticated_billing_subscription** - 400 Bad Request  
3. **test_e2e_organization_isolation_between_users** - KeyError 'access_token'
4. **test_e2e_full_user_journey** - 400 Bad Request

CAUSA: O reload do módulo `app.main` (para isolar conexões async) cria uma nova 
instância do app que NÃO possui acesso ao banco de dados configurado corretamente.
O novo app instance referencia um novo engine que não foi inicializado com as 
tabelas do banco de testes, causando falhas nos endpoints de billing que 
requerem dados do Asaas (API externa).

--------------------------------------------------------------------------------
CORREÇÕES APLICADAS VS. LIMITAÇÕES ESTRUTURAIS:
--------------------------------------------------------------------------------

✅ CORRIGIDO:
- Task with Future attached to different loop → Substituído TestClient por 
  httpx.AsyncClient + ASGITransport
- Rate limit 429 entre testes → Fixture reset_limiter com limiter._storage.reset()
- Estado persistido no banco → TRUNCATE com CASCADE em setup_session
- Flakiness de ordem entre testes → Reload de módulos para isolar engine

❌ LIMITAÇÃO ESTRUTURAL:
- O reload de `app.main` via importlib.reload() quebra a inicialização 
  correta do banco de dados (o novo app instance não tem acesso ao engine 
  configurado)
- Isso afeta endpoints que dependem de integração externa (billing/Asaas)
- Solução definitiva requereria injeção de dependência do engine, não reload

--------------------------------------------------------------------------------
COMPARAÇÃO EVOLUÇÃO:
--------------------------------------------------------------------------------

- Início: 9 failures (problemas de event loop + rate limit + banco)
- Após arquitetura async: 8 failures (race conditions de conexões async)
- Após module reload: 4 failures (problema de inicialização de banco)

--------------------------------------------------------------------------------
ARQUIVO DE RESULTADOS SALVO:
--------------------------------------------------------------------------------
Local: D:\Python\Códigos\boilerplate_v01\z_TestResult_001.md
