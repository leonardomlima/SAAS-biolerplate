def test_orgs(client):
    assert client.get("/api/v1/organizations/").status_code == 200
