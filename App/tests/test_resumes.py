import io
from app.tests.helpers import auth_headers

MINIMAL_PDF = (
    b"%PDF-1.4\n"
    b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
    b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
    b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Resources<<>>>>endobj\n"
    b"trailer<</Size 4/Root 1 0 R>>\n"
    b"%%EOF"
)

def test_upload_rejects_unsupported_type(client):
    headers = auth_headers(client)
    response = client.post('/api/resumes', headers=headers, files={'file': ('notes.txt', b'hello', 'text/plain')})
    assert response.status_code == 415

def test_upload_rejects_invalid_pdf_signature(client):
    headers = auth_headers(client)
    response = client.post('/api/resumes', headers=headers, files={'file': ('resume.pdf', b'not a real pdf', 'application/pdf')})
    assert response.status_code == 415

def test_upload_list_get_and_delete(client):
    headers = auth_headers(client)
    uploaded = client.post('/api/resumes', headers=headers, files={'file': ('resume.pdf', MINIMAL_PDF, 'application/pdf')})
    assert uploaded.status_code == 201
    resume_id = uploaded.json()['data']['id']
    listed = client.get('/api/resumes', headers=headers)
    assert listed.status_code == 200 and listed.json()['data']['pagination']['total_items'] == 1
    fetched = client.get(f'/api/resumes/{resume_id}', headers=headers)
    assert fetched.status_code == 200
    deleted = client.delete(f'/api/resumes/{resume_id}', headers=headers)
    assert deleted.status_code == 204
    assert client.get(f'/api/resumes/{resume_id}', headers=headers).status_code == 404

def test_resumes_require_authentication(client):
    assert client.get('/api/resumes').status_code == 401
