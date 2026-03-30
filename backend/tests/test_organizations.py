
def test_create_and_list_orgs(client):
    payload = {
        "email": "org-owner@example.com",
        "password": "supersecret123",
        "organization_name": "Primary Org",
    }
    register_response = client.post("/api/v1/auth/register", json=payload)
    assert register_response.status_code == 200
    access_token = register_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {access_token}"}

    create_response = client.post(
        "/api/v1/organizations/",
        json={"name": "Secondary Org"},
        headers=auth_headers,
    )
    assert create_response.status_code == 200

    list_response = client.get("/api/v1/organizations/", headers=auth_headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) >= 1
