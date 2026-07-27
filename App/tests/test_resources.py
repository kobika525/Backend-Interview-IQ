from app.tests.helpers import auth_headers, seed_learning_resource

def test_list_complete_and_bookmark_resource(client):
    resource_id = seed_learning_resource()
    headers = auth_headers(client)
    listed = client.get('/api/resources', headers=headers)
    assert listed.status_code == 200 and listed.json()['data'][0]['completed'] is False
    completed = client.post(f'/api/resources/{resource_id}/complete', headers=headers)
    assert completed.status_code == 200 and completed.json()['data']['completed'] is True
    bookmarked = client.post(f'/api/resources/{resource_id}/bookmark', headers=headers)
    assert bookmarked.status_code == 200 and bookmarked.json()['data']['bookmarked'] is True

def test_resource_action_not_found(client):
    headers = auth_headers(client)
    assert client.post('/api/resources/999/complete', headers=headers).status_code == 404
