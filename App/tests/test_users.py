def auth(client):
    client.post('/api/auth/register',json={'full_name':'Demo User','email':'user@example.com','password':'Strong@123'})
    token=client.post('/api/auth/login',json={'email':'user@example.com','password':'Strong@123'}).json()['data']['access_token']
    return {'Authorization':f'Bearer {token}'}
def test_read_and_update_profile(client):
    headers=auth(client); response=client.patch('/api/users/me/profile',headers=headers,json={'career_goal':'Become a backend engineer','weekly_learning_target':8})
    assert response.status_code==200; assert response.json()['data']['weekly_learning_target']==8
def test_complete_onboarding_requires_fields(client):
    headers=auth(client); assert client.post('/api/users/me/onboarding/complete',headers=headers).status_code==400
def test_onboarding_flow(client):
    headers=auth(client)
    saved=client.put('/api/users/me/onboarding',headers=headers,json={'career_goal':'Backend engineer','experience_level':'BEGINNER','preferred_interview_mode':'TEXT','weekly_learning_target':5,'current_skills':['Python','FastAPI']})
    assert saved.status_code==200; assert len(saved.json()['data']['current_skills'])==2
    completed=client.post('/api/users/me/onboarding/complete',headers=headers); assert completed.status_code==200; assert completed.json()['data']['onboarding_completed'] is True
def test_profile_requires_authentication(client):
    assert client.get('/api/users/me/profile').status_code==401
