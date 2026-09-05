import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint,method", [
    ("/api/v1/users/me", "GET"),
    ("/api/v1/users/", "GET"),
    ("/api/v1/organizations/", "GET"),
    ("/api/v1/organizations/", "POST"),
    ("/api/v1/billing/checkout", "POST"),
    ("/api/v1/billing/subscription", "GET"),
    ("/api/v1/billing/portal", "POST"),
])
async def test_endpoint_requires_authentication(client, endpoint, method):
    if method == "GET":
        response = await client.get(endpoint)
    else:
        response = await client.post(endpoint, json={})
    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint,method", [
    ("/api/v1/users/me", "GET"),
    ("/api/v1/users/", "GET"),
    ("/api/v1/organizations/", "GET"),
    ("/api/v1/organizations/", "POST"),
    ("/api/v1/billing/checkout", "POST"),
    ("/api/v1/billing/subscription", "GET"),
    ("/api/v1/billing/portal", "POST"),
])
async def test_endpoint_rejects_invalid_token(client, endpoint, method):
    headers = {"Authorization": "Bearer invalid_token_12345"}
    if method == "GET":
        response = await client.get(endpoint, headers=headers)
    else:
        response = await client.post(endpoint, json={}, headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint,method", [
    ("/api/v1/users/me", "GET"),
    ("/api/v1/users/", "GET"),
    ("/api/v1/organizations/", "GET"),
    ("/api/v1/organizations/", "POST"),
    ("/api/v1/billing/checkout", "POST"),
    ("/api/v1/billing/subscription", "GET"),
    ("/api/v1/billing/portal", "POST"),
])
async def test_endpoint_rejects_malformed_header(client, endpoint, method):
    headers = {"Authorization": "NotBearer token"}
    if method == "GET":
        response = await client.get(endpoint, headers=headers)
    else:
        response = await client.post(endpoint, json={}, headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint,payload,expected_status", [
    ("/api/v1/auth/register", {"email": "test@test.com"}, 422),
    ("/api/v1/auth/register", {"password": "pass123"}, 422),
    ("/api/v1/auth/login", {"email": "test@test.com"}, 422),
    ("/api/v1/auth/login", {}, 422),
])
async def test_register_login_validation(client, endpoint, payload, expected_status):
    response = await client.post(endpoint, json=payload)
    assert response.status_code == expected_status


@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint,payload", [
    ("/api/v1/auth/login", {"email": "not-an-email", "password": "pass"}),
    ("/api/v1/auth/login", {"email": "test@test.com", "password": ""}),
])
async def test_login_email_format_validation(client, endpoint, payload):
    response = await client.post(endpoint, json=payload)
    assert response.status_code in {401, 422}


@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint", [
    "/api/v1/auth/refresh",
])
async def test_refresh_requires_payload(client, endpoint):
    response = await client.post(endpoint, json={})
    assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint,payload", [
    ("/api/v1/auth/refresh", {"refresh_token": "invalid.token"}),
    ("/api/v1/auth/refresh", {"refresh_token": "this.is.wrong"}),
])
async def test_refresh_rejects_invalid_token(client, endpoint, payload):
    response = await client.post(endpoint, json=payload)
    assert response.status_code in {401, 422}


@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint", [
    "/api/v1/billing/plans",
    "/api/v1/health",
])
async def test_public_endpoints_accessible(client, endpoint):
    response = await client.get(endpoint)
    assert response.status_code in {200, 404}


@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint", [
    "/api/v1/billing/plans",
    "/api/v1/health",
])
async def test_public_endpoints_no_auth_required(client, endpoint):
    response = await client.get(endpoint)
    assert response.status_code in {200, 404}
    assert response.status_code != 401