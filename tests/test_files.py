from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.main import api

client = TestClient(api)

def test_file_upload():
    with open("tests/data/test_file.csv", "rb") as f:
        response = client.post(
          "/files",
          files = { "file": ("test_file.csv", f, "text/csv")}
        )

    assert response.status_code == 200
    assert response.json() == {
      "filename": "test_file.csv",
      "content_type": "text/csv",
      "size": 29
    }

def test_file_list():
    response = client.get("/files")
    assert response.json() == ["test_file.csv"]