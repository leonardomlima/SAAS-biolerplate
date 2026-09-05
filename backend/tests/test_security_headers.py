import pytest


@pytest.mark.asyncio
async def test_security_headers_present(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert "default-src 'self'" in response.headers["content-security-policy"]