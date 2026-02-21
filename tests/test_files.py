from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
import os
from api.main import api

client = TestClient(api)

@pytest.mark.parametrize(
    "test_file_path,test_mime,expected_status_code,expected_response",
    [
        ("tests/data/test_file.csv", "text/csv", 200, {
            "filename": "test_file.csv",
            "content_type": "text/csv",
            "size": 29
        }),
        ("tests/data/invalid_file.txt", "text/txt", 415, {"detail": "Invalid file type"})
    ]
)
def test_file_upload(test_file_path, test_mime, expected_status_code, expected_response):
    with open(test_file_path, "rb") as f:
        test_file_name = os.path.basename(test_file_path)
        response = client.post(
          "/files",
          files = { "file": (test_file_name, f, test_mime)}
        )

    assert response.status_code == expected_status_code
    assert response.json() == expected_response

def test_file_list():
    response = client.get("/files")
    assert response.json() == ["test_file.csv"]

@pytest.mark.parametrize(
    "filename,expected_code,expected_text",
    [
        ("test_file.csv", 200, "col1,col2,col3\nval1,val2,val3"),
        ("invalid_file.csv", 404, '{"detail":"Not Found"}')
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
        ("invalid_file.csv", 404, '{"detail":"Not Found"}')
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
