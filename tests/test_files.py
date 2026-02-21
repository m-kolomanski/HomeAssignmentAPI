from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
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

@pytest.mark.parametrize(
    "filename,expected_code,expected_text",
    [
        ("test_file.csv", 200, "col1,col2,col3\nval1,val2,val3"),
        ("invalid_file.csv", 404, "")
    ]
)
def test_get_file(filename, expected_code, expected_text):
    response = client.get(f"/files/{filename}")

    assert response.status_code == expected_code
    assert response.text == expected_text

@pytest.mark.parametrize(
    "filename,expected_code,expected_text",
    [
        ("test_file.csv", 200, "col1,col2,col3\nval1,val2,val3\nval4,val5,val6"),
        ("invalid_file.csv", 404, None)
    ]
)
def test_update_file(filename, expected_code, expected_text):
    with open("tests/data/test_file2.csv", "rb") as f:
        response = client.put(
          f"/files/{filename}",
          files = { "file": ("test_file.csv", f, "text/csv")}
        )

    assert response.status_code == expected_code

    if response.status_code == 200:
        assert response.json() == {
            "filename": "test_file.csv",
            "content_type": "text/csv",
            "size": 44
        }

        file_response = client.get(f"/files/{filename}")
        assert file_response.text == expected_text
