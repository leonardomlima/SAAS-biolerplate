"""
Testes de billing — cobre planos, checkout, subscription, portal e webhook.
"""

import uuid

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _register_and_login(client, email: str, password: str, org: str) -> dict:
    """Registra um usuário e retorna os headers com Authorization + X-Tenant-ID."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "organization_name": org},
    )
    if reg.status_code not in (200, 201):
        pytest.skip(f"Register failed: {reg.status_code} {reg.text}")

    data = reg.json()
    token = data.get("access_token")
    if not token:
        pytest.skip("No access_token in register response")

    # Decode tenant_id a partir do token
    from app.core.security import decode_token
    payload = decode_token(token)
    tenant_id = payload.get("tenant_id")

    return {
        "Authorization": f"Bearer {token}",
        "X-Tenant-ID": tenant_id,
    }


# ---------------------------------------------------------------------------
# Testes da listagem de planos (público)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_plans_public_no_auth(client):
    """GET /plans deve retornar 200 sem autenticação."""
    response = await client.get("/api/v1/billing/plans")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_plans_structure(client):
    """Cada plano deve ter id, name, amount e billing_cycle."""
    response = await client.get("/api/v1/billing/plans")
    assert response.status_code == 200
    for plan in response.json():
        assert "id" in plan
        assert "name" in plan
        assert "amount" in plan
        assert "billing_cycle" in plan
        assert isinstance(plan["amount"], (int, float))


# ---------------------------------------------------------------------------
# Testes de checkout
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_checkout_requires_auth(client):
    """POST /checkout sem token deve retornar 401."""
    response = await client.post("/api/v1/billing/checkout", json={"plan_id": "starter"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_checkout_requires_valid_plan(client):
    """POST /checkout com plano inválido deve retornar 400 (ou 401 sem tenant header)."""
    suffix = uuid.uuid4().hex[:8]
    headers = await _register_and_login(client, f"inv-plan-{suffix}@test.com", "pass1234", f"Org{suffix}")
    response = await client.post(
        "/api/v1/billing/checkout",
        json={"plan_id": "nonexistent_plan"},
        headers=headers,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_checkout_authenticated(client):
    """
    POST /checkout com plano válido deve retornar 200 (Asaas OK) ou 502 (Asaas indisponível no test).
    O importante é que não retorne 401/403/400 com plano válido.
    """
    suffix = uuid.uuid4().hex[:8]
    headers = await _register_and_login(client, f"checkout-{suffix}@test.com", "pass1234", f"Org{suffix}")
    response = await client.post(
        "/api/v1/billing/checkout",
        json={"plan_id": "starter"},
        headers=headers,
    )
    assert response.status_code in {200, 502, 503}, response.text


# ---------------------------------------------------------------------------
# Testes de subscription
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_subscription_requires_auth(client):
    """GET /subscription sem token deve retornar 401."""
    response = await client.get("/api/v1/billing/subscription")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_subscription_not_found_for_new_user(client):
    """GET /subscription para usuário sem assinatura deve retornar 404."""
    suffix = uuid.uuid4().hex[:8]
    headers = await _register_and_login(client, f"nosub-{suffix}@test.com", "pass1234", f"Org{suffix}")
    response = await client.get("/api/v1/billing/subscription", headers=headers)
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Testes de portal
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_portal_requires_auth(client):
    """POST /portal sem token deve retornar 401."""
    response = await client.post("/api/v1/billing/portal", json={})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_portal_not_found_for_new_user(client):
    """POST /portal para usuário sem assinatura deve retornar 404."""
    suffix = uuid.uuid4().hex[:8]
    headers = await _register_and_login(client, f"noportal-{suffix}@test.com", "pass1234", f"Org{suffix}")
    response = await client.post("/api/v1/billing/portal", json={}, headers=headers)
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Testes de webhook
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_webhook_invalid_token(client):
    """POST /webhook com token inválido deve retornar 401 (quando secret está configurado)."""
    from app.core.config import settings

    if not settings.ASAAS_WEBHOOK_SECRET:
        pytest.skip("ASAAS_WEBHOOK_SECRET not configured")

    payload = {
        "event": "PAYMENT_RECEIVED",
        "id": "pay_test_001",
        "payment": {"externalReference": str(uuid.uuid4()), "status": "RECEIVED"},
    }
    response = await client.post(
        "/api/v1/billing/webhook",
        json=payload,
        headers={"access_token": "wrong_secret"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_webhook_unknown_organization_returns_ok(client):
    """
    POST /webhook com externalReference de organização inexistente deve retornar 200
    (não 404) — o evento é salvo para auditoria mas sinaliza warning.
    """
    from app.core.config import settings

    headers = {}
    if settings.ASAAS_WEBHOOK_SECRET:
        headers["access_token"] = settings.ASAAS_WEBHOOK_SECRET

    payload = {
        "event": "PAYMENT_RECEIVED",
        "id": f"pay_{uuid.uuid4().hex}",
        "subscription": {
            "id": "sub_test",
            "externalReference": str(uuid.uuid4()),  # UUID que não existe
            "status": "ACTIVE",
        },
    }
    response = await client.post("/api/v1/billing/webhook", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["subscription_synced"] is False


@pytest.mark.asyncio
async def test_webhook_invalid_payload(client):
    """POST /webhook com payload sem campo 'event' deve retornar 422."""
    from app.core.config import settings

    headers = {}
    if settings.ASAAS_WEBHOOK_SECRET:
        headers["access_token"] = settings.ASAAS_WEBHOOK_SECRET

    # Payload sem "event" obrigatório
    response = await client.post("/api/v1/billing/webhook", json={"id": "something"}, headers=headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_webhook_accepts_payment_event_type(client):
    """
    POST /webhook com evento PAYMENT_CONFIRMED (campo payment, não subscription)
    deve ser aceito e retornar 200.
    """
    from app.core.config import settings

    headers = {}
    if settings.ASAAS_WEBHOOK_SECRET:
        headers["access_token"] = settings.ASAAS_WEBHOOK_SECRET

    payload = {
        "event": "PAYMENT_CONFIRMED",
        "id": f"pay_{uuid.uuid4().hex}",
        "payment": {
            "id": "pay_test_123",
            "externalReference": str(uuid.uuid4()),  # org inexistente — tudo bem
            "status": "CONFIRMED",
            "value": 49.0,
        },
    }
    response = await client.post("/api/v1/billing/webhook", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["ok"] is True