from app.database import SessionLocal
from app.models.platform import Notification
from app.tests.helpers import auth_headers

def _seed_notification(user_id, title='Welcome'):
    db = SessionLocal()
    try:
        n = Notification(user_id=user_id, type='SYSTEM', title=title, message='Hello there')
        db.add(n); db.commit(); db.refresh(n)
        return n.id
    finally:
        db.close()

def _current_user_id(client, headers):
    return client.get('/api/auth/me', headers=headers).json()['data']['id']

def test_list_mark_read_and_delete_notification(client):
    headers = auth_headers(client)
    user_id = _current_user_id(client, headers)
    notification_id = _seed_notification(user_id)
    listed = client.get('/api/notifications', headers=headers)
    assert listed.status_code == 200 and len(listed.json()['data']) == 1
    unread = client.get('/api/notifications/unread-count', headers=headers)
    assert unread.json()['data']['count'] == 1
    marked = client.patch(f'/api/notifications/{notification_id}/read', headers=headers)
    assert marked.status_code == 200 and marked.json()['data']['is_read'] is True
    deleted = client.delete(f'/api/notifications/{notification_id}', headers=headers)
    assert deleted.status_code == 200

def test_mark_all_read(client):
    headers = auth_headers(client)
    user_id = _current_user_id(client, headers)
    _seed_notification(user_id, 'One'); _seed_notification(user_id, 'Two')
    response = client.patch('/api/notifications/read-all', headers=headers)
    assert response.status_code == 200 and response.json()['data']['updated'] == 2

def test_notifications_require_authentication(client):
    assert client.get('/api/notifications').status_code == 401
