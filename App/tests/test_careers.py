from app.tests.helpers import auth_headers, seed_career_role, seed_skill_for_role

def test_list_roles(client):
    seed_career_role()
    response = client.get('/api/careers/roles')
    assert response.status_code == 200
    assert len(response.json()['data']) == 1

def test_role_not_found(client):
    assert client.get('/api/careers/roles/999').status_code == 404

def test_generate_match_and_skill_gap(client):
    role_id = seed_career_role()
    seed_skill_for_role(role_id, 'Python', required=True)
    headers = auth_headers(client)
    match = client.post('/api/careers/matches/generate', headers=headers, json={'role_id': role_id})
    assert match.status_code == 201
    assert match.json()['data']['role_id'] == role_id
    listed = client.get('/api/careers/matches', headers=headers)
    assert listed.status_code == 200 and len(listed.json()['data']) == 1
    gap = client.post('/api/careers/skill-gap', headers=headers, json={'role_id': role_id})
    assert gap.status_code == 201
    assert 'readiness_score' in gap.json()['data']
