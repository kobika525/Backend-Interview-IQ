def register(client,email='user@example.com',password='Strong@123'):
    return client.post('/api/auth/register',json={'full_name':'Demo User','email':email,'password':password})
def login(client,email='user@example.com',password='Strong@123'):
    return client.post('/api/auth/login',json={'email':email,'password':password})
def test_registration_success(client):
    response=register(client); assert response.status_code==201; assert response.json()['data']['email']=='user@example.com'
def test_duplicate_email(client):
    register(client); response=register(client); assert response.status_code==409
def test_weak_password(client):
    response=register(client,password='password'); assert response.status_code==422
def test_login_and_protected_me(client):
    register(client); signed=login(client); assert signed.status_code==200
    token=signed.json()['data']['access_token']; me=client.get('/api/auth/me',headers={'Authorization':f'Bearer {token}'})
    assert me.status_code==200; assert me.json()['data']['role']=='USER'
def test_wrong_password(client):
    register(client); assert login(client,password='Wrong@123').status_code==401
def test_refresh_rotation_and_reuse_detection(client):
    register(client); first=login(client).json()['data']['refresh_token']
    rotated=client.post('/api/auth/refresh',json={'refresh_token':first}); assert rotated.status_code==200
    reused=client.post('/api/auth/refresh',json={'refresh_token':first}); assert reused.status_code==401; assert reused.json()['error']['code']=='REFRESH_TOKEN_REUSE'
def test_password_reset_does_not_reveal_unknown_email(client):
    response=client.post('/api/auth/forgot-password',json={'email':'missing@example.com'}); assert response.status_code==200; assert response.json()['data']=={}
def test_password_reset_flow_in_development(client):
    register(client); response=client.post('/api/auth/forgot-password',json={'email':'user@example.com'}); token=response.json()['data']['development_reset_token']
    reset=client.post('/api/auth/reset-password',json={'token':token,'new_password':'Changed@123'}); assert reset.status_code==200
    assert login(client,password='Changed@123').status_code==200
def test_email_verification_flow(client):
    created=register(client).json()['data']; token=created['development_verification_token']
    verified=client.post('/api/auth/verify-email',json={'token':token}); assert verified.status_code==200; assert verified.json()['data']['email_verified'] is True
