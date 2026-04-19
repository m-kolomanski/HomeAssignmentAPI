import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import db_get
from backend.files.models import File
from pathlib import Path
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from backend.config import settings


@pytest.fixture(autouse=True)
def db_session():
    test_engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(test_engine)

    with Session(test_engine) as session:
        yield session

    test_engine.dispose()


@pytest.fixture
def client(db_session):
    def _db_get():
        yield db_session

    app.dependency_overrides[db_get] = _db_get

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def file_storage(tmp_path):
    tmp_storage_path = tmp_path / "userfiles"
    tmp_storage_path.mkdir()
    settings.FILE_STORAGE = tmp_storage_path
    yield settings.FILE_STORAGE


@pytest.fixture
def generate_csv(tmp_path, file_storage, db_session):
    def _generate_csv(
        name: str = "test_file.csv", cols: int = 3, rows: int = 2, insert: bool = False
    ) -> Path:
        # Generate file contents
        headers = ",".join((f"col-{c}" for c in range(cols)))
        csv_rows = [headers]
        for r in range(rows):
            row = ",".join((f"val-{r}-{c}" for c in range(cols)))
            csv_rows.append(row)

        csv_text = "\n".join(csv_rows)

        # Write CSV file to temp path
        # If insert == True, write directly to file storage to simulate file being present in the database
        if insert:
            csv_path = file_storage / name

            db_session.add(
                File(
                    filename=name,
                    content_type="text/csv",
                    size=len(csv_text),
                    ncol=cols,
                    nrow=rows,
                )
            )
            db_session.commit()

        else:
            csv_path = tmp_path / "input" / name
            csv_path.parent.mkdir(exist_ok=True)

        csv_path.write_text(csv_text)

        return csv_path

    return _generate_csv
