from app.tests.helpers import auth_headers, seed_subscription_plan
from app.database import SessionLocal
from app.models.platform import UserSubscription

def test_list_plans(client):
    seed_subscription_plan('Free', 0)
    response = client.get('/api/subscriptions/plans')
    assert response.status_code == 200 and response.json()['data'][0]['name'] == 'Free'

def test_current_and_demo_upgrade(client):
    free_id = seed_subscription_plan('Free', 0)
    pro_id = seed_subscription_plan('Pro', 25)
    headers = auth_headers(client)
    user_id = client.get('/api/auth/me', headers=headers).json()['data']['id']
    db = SessionLocal()
    try:
        db.add(UserSubscription(user_id=user_id, plan_id=free_id, status='ACTIVE')); db.commit()
    finally:
        db.close()
    current = client.get('/api/subscriptions/current', headers=headers)
    assert current.status_code == 200 and current.json()['data']['plan']['name'] == 'Free'
    upgraded = client.post('/api/subscriptions/demo-upgrade', headers=headers, params={'plan_id': pro_id})
    assert upgraded.status_code == 200
    assert client.get('/api/subscriptions/current', headers=headers).json()['data']['plan']['name'] == 'Pro'
