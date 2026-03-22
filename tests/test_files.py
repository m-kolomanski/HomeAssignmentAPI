import shutil
import pytest

@pytest.mark.parametrize(
    ("filename", "ncol", "nrow", "size"),
    [
        ("test_file.csv", 3, 2, 65),
        ("test_file_no_rows.csv", 3, 0, 17),
        ("test_file_mid.csv", 5, 10, 429),
        ("test_file_big.csv", 30, 100, 28899)
    ]
)
def test_file_upload__ok(client, generate_csv, filename, ncol, nrow, size):
    test_file = generate_csv(filename, ncol, nrow)

    with open(test_file, "rb") as f:
        response = client.post(
            "/files",
            files = { "file": (filename, f, "text/csv")}
        )

    assert response.status_code == 200
    assert response.json() == {
            "filename": filename,
            "content_type": "text/csv",
            "size": size
        }
    
def test_file_upload__file_exists(file_storage, client, generate_csv):
    test_file = generate_csv()
    shutil.copy(test_file, file_storage)

    with open(test_file, "rb") as f:
        response = client.post(
            "/files",
            files = { "file": ("test_file.csv", f, "text/csv") }
        )

    assert response.status_code == 409

def test_file_upload__invalid_mime(client, generate_csv):
    test_file = generate_csv()
    
    with open(test_file, "rb") as f:
        response = client.post(
            "/files",
            files = { "file": ("some_file.csv", f, "image/png") }
        )

    assert response.status_code == 415

@pytest.mark.parametrize(
    ("filenames"),
    [
        (["single_file.csv"]),
        (["first_file.csv", "second_file.csv"]),
        ([f"file-{n}.csv" for n in range(20)])
    ]
)
def test_file_list(file_storage, client, generate_csv, filenames):
    for file in filenames:
        test_file = generate_csv(file)
        shutil.copy(test_file, file_storage)

    response = client.get("/files")
    assert response.status_code == 200
    assert response.json().sort() == filenames.sort()

def test_get_file__ok(file_storage, client, generate_csv):
    test_file = generate_csv()
    shutil.copy(test_file, file_storage)

    response = client.get("/files/test_file.csv")

    assert response.status_code == 200
    assert response.text == "col-0,col-1,col-2\nval-0-0,val-0-1,val-0-2\nval-1-0,val-1-1,val-1-2"

def test_get_file__missing(client):
    response = client.get("/files/nonexistent_file.csv")

    assert response.status_code == 404

def test_update_file__ok(file_storage, client, generate_csv):
    test_file_to_overwrite = generate_csv(name = "test_file.csv", cols = 1, rows = 3)
    shutil.copy(test_file_to_overwrite, file_storage)

    test_file = generate_csv(name = "new_test_file.csv", cols = 5, rows = 1)

    with open(test_file, "rb") as f:
        response = client.put(
            "/files/test_file.csv",
            files = { "file": ("test_file.csv", f, "text/csv") }
        )

    assert response.status_code == 200
    assert response.json() == {
            "filename": "test_file.csv",
            "content_type": "text/csv",
            "size": 69
        }

def test_update_file__missing(client, generate_csv):
    test_file = generate_csv(name = "new_test_file.csv", cols = 5, rows = 1)

    with open(test_file, "rb") as f:
        response = client.put(
            "/files/nonexistent_file.csv",
            files = { "file": ("test_file.csv", f, "text/csv") }
        )

    assert response.status_code == 404
