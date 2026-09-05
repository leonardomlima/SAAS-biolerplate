import pytest

from app.core.config import settings
from app.core.security import decode_token


def _auth_headers_with_tenant(access_token: str) -> dict[str, str]:
    token_data = decode_token(access_token)
    tenant_id = token_data["tenant_id"]
    return {
        "Authorization": f"Bearer {access_token}",
        "X-Tenant-ID": tenant_id,
    }


@pytest.mark.asyncio
async def test_e2e_billing_flow_public_plans_only(client):
    plans_response = await client.get("/api/v1/billing/plans")
    assert plans_response.status_code == 200
    plans_data = plans_response.json()
    assert len(plans_data) > 0

    plan = plans_data[0]
    assert "id" in plan
    assert "name" in plan
    assert "amount" in plan


@pytest.mark.asyncio
async def test_e2e_invalid_token_propagates_to_all_endpoints(client):
    headers = {"Authorization": "Bearer valid_format_but.invalid.token"}

    users_response = await client.get("/api/v1/users/me", headers=headers)
    assert users_response.status_code == 401

    list_users_response = await client.get("/api/v1/users/", headers=headers)
    assert list_users_response.status_code == 401

    orgs_response = await client.get("/api/v1/organizations/", headers=headers)
    assert orgs_response.status_code == 401

    checkout_response = await client.post(
        "/api/v1/billing/checkout",
        json={"plan_id": "starter"},
        headers=headers,
    )
    assert checkout_response.status_code == 401


@pytest.mark.asyncio
async def test_e2e_public_endpoints_work_without_auth(client):
    health_response = await client.get("/api/v1/health")
    assert health_response.status_code in {200, 404}

    plans_response = await client.get("/api/v1/billing/plans")
    assert plans_response.status_code == 200

    plans_data = plans_response.json()
    assert isinstance(plans_data, list)
    assert len(plans_data) > 0


@pytest.mark.asyncio
async def test_e2e_register_login_refresh_me(client):
    register_payload = {
        "email": "e2e@example.com",
        "password": "securepass123",
        "organization_name": "E2E Org",
    }
    register_response = await client.post(
        "/api/v1/auth/register", json=register_payload
    )
    assert register_response.status_code == 200
    register_data = register_response.json()
    assert "access_token" in register_data
    assert "refresh_token" in register_data
    refresh_token = register_data["refresh_token"]

    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": register_payload["email"],
            "password": register_payload["password"],
        },
    )
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "access_token" in login_data
    assert "refresh_token" in login_data

    refresh_response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_response.status_code == 200
    new_token = refresh_response.json()["access_token"]
    assert new_token

    me_response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {new_token}"},
    )
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["email"] == register_payload["email"]
    assert "id" in me_data
    assert "full_name" in me_data


@pytest.mark.asyncio
async def test_e2e_organization_create_and_list(client):
    register_payload = {
        "email": "org-e2e@test.com",
        "password": "orgpass123",
        "organization_name": "Org E2E",
    }
    register_response = await client.post(
        "/api/v1/auth/register", json=register_payload
    )
    assert register_response.status_code == 200
    access_token = register_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {access_token}"}

    create_response = await client.post(
        "/api/v1/organizations/",
        json={"name": "Second Organization"},
        headers=auth_headers,
    )
    assert create_response.status_code == 200
    org_data = create_response.json()
    assert "id" in org_data
    assert org_data["name"] == "Second Organization"

    list_response = await client.get("/api/v1/organizations/", headers=auth_headers)
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert isinstance(list_data, list)
    assert len(list_data) >= 1
    org = list_data[0]
    assert "id" in org
    assert "name" in org


@pytest.mark.asyncio
async def test_e2e_authenticated_billing_checkout(client):
    register_payload = {
        "email": "billing-e2e@test.com",
        "password": "billpass123",
        "organization_name": "Billing E2E",
    }
    register_response = await client.post(
        "/api/v1/auth/register", json=register_payload
    )
    assert register_response.status_code == 200
    access_token = register_response.json()["access_token"]
    auth_headers = _auth_headers_with_tenant(access_token)

    checkout_response = await client.post(
        "/api/v1/billing/checkout",
        json={"plan_id": "starter"},
        headers=auth_headers,
    )
    expected = {200, 502}
    if not settings.ASAAS_API_KEY:
        expected.add(503)
    assert checkout_response.status_code in expected, checkout_response.text


@pytest.mark.asyncio
async def test_e2e_authenticated_billing_subscription(client):
    register_payload = {
        "email": "sub-e2e@test.com",
        "password": "subpass123",
        "organization_name": "Sub E2E",
    }
    register_response = await client.post(
        "/api/v1/auth/register", json=register_payload
    )
    assert register_response.status_code == 200
    access_token = register_response.json()["access_token"]
    auth_headers = _auth_headers_with_tenant(access_token)

    subscription_response = await client.get(
        "/api/v1/billing/subscription",
        headers=auth_headers,
    )
    assert subscription_response.status_code in {200, 404}, subscription_response.text


@pytest.mark.asyncio
async def test_e2e_organization_isolation_between_users(client):
    payload1 = {
        "email": "user1@test.com",
        "password": "UserPass123",
        "organization_name": "User1 Org",
    }
    reg1 = await client.post("/api/v1/auth/register", json=payload1)
    assert reg1.status_code == 200, reg1.text
    token1 = reg1.json()["access_token"]

    payload2 = {
        "email": "user2@test.com",
        "password": "UserPass123",
        "organization_name": "User2 Org",
    }
    reg2 = await client.post("/api/v1/auth/register", json=payload2)
    assert reg2.status_code == 200, reg2.text
    token2 = reg2.json()["access_token"]

    await client.post(
        "/api/v1/organizations/",
        json={"name": "Private Org"},
        headers={"Authorization": f"Bearer {token1}"},
    )

    orgs1 = await client.get(
        "/api/v1/organizations/", headers={"Authorization": f"Bearer {token1}"}
    )
    orgs2 = await client.get(
        "/api/v1/organizations/", headers={"Authorization": f"Bearer {token2}"}
    )

    names1 = {org["name"] for org in orgs1.json()}
    names2 = {org["name"] for org in orgs2.json()}

    assert "Private Org" in names1
    assert "Private Org" not in names2


@pytest.mark.asyncio
async def test_e2e_full_user_journey(client):
    register_payload = {
        "email": "journey@test.com",
        "password": "journeypass123",
        "organization_name": "Journey Org",
    }
    register_response = await client.post(
        "/api/v1/auth/register", json=register_payload
    )
    assert register_response.status_code == 200
    token = register_response.json()["access_token"]
    auth_headers = _auth_headers_with_tenant(token)

    me_response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200

    orgs_response = await client.get(
        "/api/v1/organizations/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert orgs_response.status_code == 200

    checkout_response = await client.post(
        "/api/v1/billing/checkout",
        json={"plan_id": "growth"},
        headers=auth_headers,
    )
    assert checkout_response.status_code in {200, 502}, checkout_response.text

    portal_response = await client.post(
        "/api/v1/billing/portal",
        json={},
        headers=auth_headers,
    )
    assert portal_response.status_code in {200, 404}, portal_response.text
