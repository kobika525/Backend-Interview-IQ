from app.tests.helpers import auth_headers, seed_career_role, seed_skill_for_role

def test_list_skills_and_upsert_mine(client):
    role_id = seed_career_role()
    skill_id = seed_skill_for_role(role_id, 'Python')
    headers = auth_headers(client)
    listed = client.get('/api/skills', headers=headers)
    assert listed.status_code == 200 and len(listed.json()['data']) == 1
    upserted = client.put(f'/api/skills/mine/{skill_id}', headers=headers, json={'proficiency': 3})
    assert upserted.status_code == 200 and upserted.json()['data']['proficiency'] == 3
    mine = client.get('/api/skills/mine', headers=headers)
    assert mine.status_code == 200 and mine.json()['data'][0]['proficiency'] == 3
