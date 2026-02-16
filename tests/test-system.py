from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.main import api

client = TestClient(api)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
