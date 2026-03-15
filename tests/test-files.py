def test_file_upload__ok(client, generate_csv):
    test_file = generate_csv()

    with open(test_file, "rb") as f:
        response = client.post(
            "/files",
            files = { "file": ("test_file.csv", f, "text/csv")}
        )

    assert response.status_code == 200
    assert response.json() == {
            "filename": "test_file.csv",
            "content_type": "text/csv",
            "size": 65
        }
    
def test_file_upload__file_exists(client, generate_csv):
    test_file = generate_csv()

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

def test_file_list(client):
    response = client.get("/files")
    assert response.json() == ["test_file.csv"]

def test_get_file__ok(client):
    response = client.get("/files/test_file.csv")

    assert response.status_code == 200
    assert response.text == "col-0,col-1,col-2\nval-0-0,val-0-1,val-0-2\nval-1-0,val-1-1,val-1-2"

def test_get_file__missing(client):
    response = client.get("/files/nonexistent_file.csv")

    assert response.status_code == 404

def test_update_file__ok(client, generate_csv):
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
