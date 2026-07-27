from app.database import SessionLocal
from app.models.platform import BillingRecord
from app.tests.helpers import auth_headers

def test_list_billing_records(client):
    headers = auth_headers(client)
    user_id = client.get('/api/auth/me', headers=headers).json()['data']['id']
    db = SessionLocal()
    try:
        db.add(BillingRecord(user_id=user_id, description='Pro plan renewal', amount=25.00, currency='LKR', status='DEMO'))
        db.commit()
    finally:
        db.close()
    response = client.get('/api/billing', headers=headers)
    assert response.status_code == 200
    assert response.json()['data'][0]['description'] == 'Pro plan renewal'

def test_billing_requires_authentication(client):
    assert client.get('/api/billing').status_code == 401
