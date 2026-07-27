from app.tests.helpers import auth_headers

def test_dashboard_returns_zeroed_metrics_for_new_user(client):
    headers = auth_headers(client)
    response = client.get('/api/progress/dashboard', headers=headers)
    assert response.status_code == 200
    data = response.json()['data']
    assert data['total_interviews'] == 0
    assert 'advisory_notice' in data

def test_summary_matches_dashboard(client):
    headers = auth_headers(client)
    dashboard = client.get('/api/progress/dashboard', headers=headers).json()['data']
    summary = client.get('/api/progress/summary', headers=headers).json()['data']
    assert dashboard == summary

def test_progress_requires_authentication(client):
    assert client.get('/api/progress/dashboard').status_code == 401
