from app.tests.helpers import auth_headers, seed_career_role

def test_generate_and_complete_roadmap(client):
    role_id = seed_career_role()
    headers = auth_headers(client)
    generated = client.post('/api/roadmaps/generate', headers=headers, json={'role_id': role_id})
    assert generated.status_code == 201
    roadmap = generated.json()['data']
    assert roadmap['role_id'] == role_id and len(roadmap['items']) > 0
    item_id = roadmap['items'][0]['id']
    completed = client.post(f"/api/roadmaps/{roadmap['id']}/items/{item_id}/complete", headers=headers)
    assert completed.status_code == 200
    assert completed.json()['data']['items'][0]['completed'] is True
    listed = client.get('/api/roadmaps', headers=headers)
    assert listed.status_code == 200 and len(listed.json()['data']) == 1

def test_generate_roadmap_requires_valid_role(client):
    headers = auth_headers(client)
    assert client.post('/api/roadmaps/generate', headers=headers, json={'role_id': 999}).status_code == 404

def test_roadmaps_require_authentication(client):
    assert client.get('/api/roadmaps').status_code == 401
