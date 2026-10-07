import pytest
from pathlib import Path
from freezegun import freeze_time

from backend.file_tags.models import FileTag
from backend.tags.models import Tag


@pytest.mark.parametrize(
    ("filename", "ncol", "nrow", "size"),
    [
        ("test_file.csv", 3, 2, 65),
        ("test_file_no_rows.csv", 3, 0, 17),
        ("test_file_mid.csv", 5, 10, 429),
        ("test_file_big.csv", 30, 100, 28899),
    ],
)
@freeze_time("2026-05-10 12:00:00")
def test_file_upload__ok(client, generate_csv, filename, ncol, nrow, size):
    test_file = generate_csv(filename, ncol, nrow)

    with open(test_file, "rb") as f:
        response = client.post("/files", files={"file": (filename, f, "text/csv")})

    assert response.status_code == 200
    assert response.json() == {
        "filename": Path(filename).stem,
        "content_type": "text/csv",
        "size": size,
        "ncol": ncol,
        "nrow": nrow,
        "id": 1,
        "uploaded_at": "2026-05-10T12:00:00",
        "updated_at": "2026-05-10T12:00:00",
    }


def test_file_upload__invalid_mime(client, generate_csv):
    test_file = generate_csv()

    with open(test_file, "rb") as f:
        response = client.post(
            "/files", files={"file": ("some_file.csv", f, "image/png")}
        )

    assert response.status_code == 415


@pytest.mark.parametrize(
    ("filenames"),
    [
        (["single_file.csv"]),
        (["first_file.csv", "second_file.csv"]),
        ([f"file-{n}.csv" for n in range(20)]),
    ],
)
def test_file_list(client, generate_csv, filenames):
    expected_file_names = [Path(f).stem for f in filenames]

    for file in filenames:
        generate_csv(file, insert=True)

    response = client.get("/files")
    file_names = [x["filename"] for x in response.json()]
    assert response.status_code == 200
    assert file_names.sort() == expected_file_names.sort()


def test_file_list__name_query(client, generate_csv):
    generate_csv("searched_file", insert=True)
    generate_csv("dummy_file", insert=True)

    response = client.get("/files", params={"name": "searched"})
    result = response.json()

    assert response.status_code == 200
    assert len(result) == 1
    assert result[0]["filename"] == "searched_file"


def test_file_list__tag_query(client, generate_csv, db_session):
    generate_csv("searched_file", insert=True)
    generate_csv("dummy_file", insert=True)
    db_session.add(Tag(name="test"))
    db_session.add(Tag(name="other"))
    db_session.add(FileTag(file_id=1, tag_id=1))
    db_session.add(FileTag(file_id=2, tag_id=2))

    response = client.get("/files", params={"tags": "test"})
    result = response.json()

    assert response.status_code == 200
    assert len(result) == 1
    assert result[0]["filename"] == "searched_file"


def test_file_list__tag_query_multi(client, generate_csv, db_session):
    generate_csv("searched_file", insert=True)
    generate_csv("dummy_file", insert=True)
    db_session.add(Tag(name="test"))
    db_session.add(Tag(name="other"))
    db_session.add(FileTag(file_id=1, tag_id=1))
    db_session.add(FileTag(file_id=1, tag_id=2))
    db_session.add(FileTag(file_id=2, tag_id=2))

    response = client.get("/files", params={"tags": ["test", "other"]})
    result = response.json()

    assert response.status_code == 200
    assert len(result) == 1
    assert result[0]["filename"] == "searched_file"


def test_get_file__ok(client, generate_csv):
    generate_csv(insert=True)

    response = client.get("/files/1")

    assert response.status_code == 200
    assert (
        response.text
        == "col-0,col-1,col-2\nval-0-0,val-0-1,val-0-2\nval-1-0,val-1-1,val-1-2\n"
    )


def test_get_file__missing(client):
    response = client.get("/files/404")

    assert response.status_code == 404


@freeze_time("2026-05-10 12:00:00")
def test_update_file__ok(client, generate_csv):
    generate_csv(name="test_file.csv", cols=1, rows=3, insert=True)

    test_file = generate_csv(name="new_test_file.csv", cols=5, rows=1)

    with open(test_file, "rb") as f:
        response = client.put(
            "/files/1", files={"file": ("test_file.csv", f, "text/csv")}
        )

    assert response.status_code == 200
    assert response.json() == {
        "filename": "test_file",
        "content_type": "text/csv",
        "size": 69,
        "ncol": 5,
        "nrow": 1,
        "id": 1,
        "uploaded_at": "2026-05-10T12:00:00",
        "updated_at": "2026-05-10T12:00:00",
    }


def test_update_file__missing(client, generate_csv):
    test_file = generate_csv(name="new_test_file.csv", cols=5, rows=1)

    with open(test_file, "rb") as f:
        response = client.put(
            "/files/404",
            files={"file": ("test_file.csv", f, "text/csv")},
        )

    assert response.status_code == 404
