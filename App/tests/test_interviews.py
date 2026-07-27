from app.tests.helpers import auth_headers, seed_interview_question

def test_create_interview_requires_question_bank(client):
    headers = auth_headers(client)
    response = client.post('/api/interviews', headers=headers, json={'number_of_questions': 3})
    assert response.status_code == 400
    assert response.json()['error']['code'] == 'QUESTION_BANK_EMPTY'

def test_full_interview_flow(client):
    seed_interview_question('Tell me about yourself.', 'HR', 'HR')
    headers = auth_headers(client)
    created = client.post('/api/interviews', headers=headers, json={'number_of_questions': 1})
    assert created.status_code == 201
    session_id = created.json()['data']['id']
    started = client.post(f'/api/interviews/{session_id}/start', headers=headers)
    assert started.status_code == 200
    question = started.json()['data']['question']
    answered = client.post(f'/api/interviews/{session_id}/answers/text', headers=headers, json={'question_id': question['id'], 'answer_text': 'My background includes building web applications with FastAPI and React.'})
    assert answered.status_code == 200
    completed = client.post(f'/api/interviews/{session_id}/complete', headers=headers)
    assert completed.status_code == 200
    assert 'overall_score' in completed.json()['data']

def test_interview_requires_authentication(client):
    assert client.get('/api/interviews').status_code == 401
