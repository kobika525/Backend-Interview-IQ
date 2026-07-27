from app.database import SessionLocal
from app.models.user import User
from app.tests.helpers import auth_headers, register, login

def _promote_to_admin(email):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        user.role = 'ADMIN'
        db.commit()
    finally:
        db.close()

def test_admin_endpoints_require_admin_role(client):
    headers = auth_headers(client)
    assert client.get('/api/admin/dashboard', headers=headers).status_code == 403

def test_admin_dashboard_users_and_questions(client):
    register(client, email='admin@example.com')
    _promote_to_admin('admin@example.com')
    token = login(client, email='admin@example.com').json()['data']['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    dashboard = client.get('/api/admin/dashboard', headers=headers)
    assert dashboard.status_code == 200
    assert dashboard.json()['data']['total_users'] == 1
    users = client.get('/api/admin/users', headers=headers)
    assert users.status_code == 200 and users.json()['data'][0]['email'] == 'admin@example.com'
    questions = client.get('/api/admin/questions', headers=headers)
    assert questions.status_code == 200
