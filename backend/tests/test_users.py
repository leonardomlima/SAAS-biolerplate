def test_users_me(client):
    payload = {
        "email": "me@example.com",
        "password": "supersecret123",
        "organization_name": "Me Org",
    }
    register_response = client.post("/api/v1/auth/register", json=payload)
    assert register_response.status_code == 200
    access_token = register_response.json()["access_token"]

    me_response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == payload["email"]
