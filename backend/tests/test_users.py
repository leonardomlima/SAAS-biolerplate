def test_users(client):
    assert client.get("/api/v1/users/").status_code == 200
