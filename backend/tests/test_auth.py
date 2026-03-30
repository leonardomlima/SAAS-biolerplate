def test_register_and_login_flow(client):
    register_payload = {
        "email": "owner@example.com",
        "password": "supersecret123",
        "full_name": "Owner User",
        "organization_name": "Acme Inc",
    }
    register_response = client.post("/api/v1/auth/register", json=register_payload)
    assert register_response.status_code == 200
    register_data = register_response.json()
    assert register_data["access_token"]
    assert register_data["refresh_token"]

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": register_payload["email"], "password": register_payload["password"]},
    )
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert login_data["access_token"]
    assert login_data["refresh_token"]

    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": login_data["refresh_token"]},
    )
    assert refresh_response.status_code == 200
    assert refresh_response.json()["access_token"]
