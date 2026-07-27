from app.tests.helpers import auth_headers

def test_create_ticket_and_add_message(client):
    headers = auth_headers(client)
    created = client.post('/api/support', headers=headers, json={'subject': 'Cannot upload resume', 'category': 'Bug', 'message': 'Upload keeps failing.'})
    assert created.status_code == 201
    ticket_id = created.json()['data']['id']
    detail = client.get(f'/api/support/{ticket_id}', headers=headers)
    assert detail.status_code == 200 and len(detail.json()['data']['messages']) == 1
    replied = client.post(f'/api/support/{ticket_id}/messages', headers=headers, json={'message': 'Any update?'})
    assert replied.status_code == 201
    listed = client.get('/api/support', headers=headers)
    assert listed.status_code == 200 and len(listed.json()['data']) == 1

def test_support_ticket_not_found(client):
    headers = auth_headers(client)
    assert client.get('/api/support/999', headers=headers).status_code == 404

def test_support_requires_authentication(client):
    assert client.get('/api/support').status_code == 401
