from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_login_rate_limit_returns_client_error_for_invalid_payload():
    response = client.post("/api/v1/auth/login", json={"email": "bad", "password": "1"})
    assert response.status_code in {401, 422, 429}
