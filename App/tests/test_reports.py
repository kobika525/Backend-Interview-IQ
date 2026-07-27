def test_placeholder_health(client):
    assert client.get("/health").status_code == 200
