from app.tests.helpers import auth_headers, seed_achievement

def test_list_achievements_shows_unearned_by_default(client):
    seed_achievement()
    headers = auth_headers(client)
    response = client.get('/api/achievements', headers=headers)
    assert response.status_code == 200
    data = response.json()['data']
    assert len(data) == 1 and data[0]['earned'] is False

def test_achievements_require_authentication(client):
    assert client.get('/api/achievements').status_code == 401
