from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_docs():
    response = client.get("/docs")
    assert response.status_code == 200

def test_register():
    response = client.post("/auth/register", params={
        "email": "pytest@test.com",
        "password": "Test@1234",
        "full_name": "PyTest User"
    })
    assert response.status_code in [200, 409]  # 409 if already exists