from sqlmodel import select

from backend.file_tags.models import FileTag
from backend.tags.models import Tag


def test_tag_file__ok(client, generate_csv, db_session):
    generate_csv(name="test_file.csv", insert=True)
    db_session.add(Tag(name="test_tag"))
    db_session.add(FileTag(file_id=1, tag_id=1))

    response = client.get("/files/test_file/tags")

    assert response.status_code == 200
    assert response.json() == ["test_tag"]


def test_get_file_tags__not_found(client):
    response = client.get("/files/invalid_file/tags")

    assert response.status_code == 404
    assert response.json()["detail"] == "File 'invalid_file' not found"


def test_post_tag_file__single__ok(client, generate_csv, db_session):
    generate_csv(name="test_file.csv", insert=True)
    db_session.add(Tag(name="test_tag"))

    response = client.post("/files/test_file/tags", params={"tag_name": "test_tag"})
    file_tags = db_session.exec(select(FileTag).where(FileTag.file_id == 1)).all()

    assert response.status_code == 200
    assert response.json() == {"id": 1, "file_id": 1, "tag_id": 1}
    assert len(file_tags) == 1


def test_tag_file__multiple__ok(client, generate_csv, db_session):
    generate_csv(name="test_file.csv", insert=True)
    db_session.add(Tag(name="test_tag"))
    db_session.add(Tag(name="second_tag"))
    db_session.add(FileTag(file_id=1, tag_id=1))

    response = client.post("/files/test_file/tags", params={"tag_name": "second_tag"})
    file_tags = db_session.exec(select(FileTag).where(FileTag.file_id == 1)).all()

    assert response.status_code == 200
    assert response.json() == {"id": 2, "file_id": 1, "tag_id": 2}
    assert len(file_tags) == 2


def test_tag_file__file_not_found(client):
    response = client.post("/files/invalid_file/tags", params={"tag_name": "test_tag"})

    assert response.status_code == 404
    assert response.json()["detail"] == "File 'invalid_file' not found"


def test_tag_file__tag_not_found(client, generate_csv):
    generate_csv(name="test_file.csv", insert=True)

    response = client.post("/files/test_file/tags", params={"tag_name": "test_tag"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Tag 'test_tag' not found"


def test_tag_file__conflict(client, generate_csv, db_session):
    generate_csv(name="test_file.csv", insert=True)
    db_session.add(Tag(name="test_tag"))
    db_session.add(FileTag(file_id=1, tag_id=1))

    response = client.post("/files/test_file/tags", params={"tag_name": "test_tag"})

    assert response.status_code == 409
    assert response.json()["detail"] == "File 'test_file' already has 'test_tag' tag"


def test_untag_file__ok(client, generate_csv, db_session):
    generate_csv(name="test_file.csv", insert=True)
    db_session.add(Tag(name="test_tag"))
    db_session.add(FileTag(file_id=1, tag_id=1))

    response = client.delete("/files/test_file/tags", params={"tag_name": "test_tag"})

    assert response.status_code == 200


def test_untag_file__file_not_found(client):
    response = client.delete(
        "/files/invalid_file/tags", params={"tag_name": "test_tag"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "File 'invalid_file' not found"


def test_untag_file__tag_not_found(client, generate_csv):
    generate_csv(name="test_file.csv", insert=True)

    response = client.delete("/files/test_file/tags", params={"tag_name": "test_tag"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Tag 'test_tag' not found"


def test_untag_file__conflict(client, generate_csv, db_session):
    generate_csv(name="test_file.csv", insert=True)
    db_session.add(Tag(name="test_tag"))

    response = client.delete("/files/test_file/tags", params={"tag_name": "test_tag"})

    assert response.status_code == 409
    assert response.json()["detail"] == "File 'test_file' does not have 'test_tag' tag"
