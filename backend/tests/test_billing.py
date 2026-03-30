def test_billing(client):
    assert client.get("/api/v1/billing/plans").status_code == 200
