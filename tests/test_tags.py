import pytest
from datetime import datetime
from freezegun import freeze_time
from sqlmodel import select

from backend.tags.models import Tag


@pytest.mark.parametrize(
    ("tags_to_add", "expected_response"),
    [
        ([], []),
        (
            [Tag(name="test_tag", uploaded_at=datetime(2026, 8, 23, 12, 0, 0))],
            [{"name": "test_tag", "uploaded_at": "2026-08-23T12:00:00", "id": 1}],
        ),
        (
            [
                Tag(name="test_tag", uploaded_at=datetime(2026, 8, 23, 12, 0, 0)),
                Tag(name="other_tag", uploaded_at=datetime(2027, 1, 1, 13, 0, 1)),
            ],
            [
                {"name": "test_tag", "uploaded_at": "2026-08-23T12:00:00", "id": 1},
                {"name": "other_tag", "uploaded_at": "2027-01-01T13:00:01", "id": 2},
            ],
        ),
    ],
)
def test_get_tags__ok(client, db_session, tags_to_add, expected_response):
    for tag in tags_to_add:
        db_session.add(tag)

    response = client.get("/tags")

    assert response.status_code == 200
    assert response.json() == expected_response


@freeze_time("2026-08-23 12:00:00")
def test_post_tags__ok(client):
    response = client.post("/tags", params={"name": "test_tag"})

    assert response.status_code == 200
    assert response.json() == {
        "name": "test_tag",
        "uploaded_at": "2026-08-23T12:00:00",
        "id": 1,
    }


def test_post_tags__conflict(client, db_session):
    db_session.add(Tag(name="conflicting_tag"))

    response = client.post("/tags", params={"name": "conflicting_tag"})

    assert response.status_code == 409


def test_delete_tags__ok(client, db_session):
    db_session.add(Tag(name="tag_to_delete"))

    response = client.delete("/tags", params={"name": "tag_to_delete"})
    tag_exists = db_session.exec(
        select(Tag).where(Tag.name == "tag_to_delete")
    ).one_or_none()

    assert response.status_code == 200
    assert tag_exists is None


def test_delete_tags__not_found(client):
    response = client.delete("/tags", params={"name": "invalid_tag"})

    assert response.status_code == 404
