import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import db_get
from pathlib import Path
from sqlmodel import Session, SQLModel, create_engine
import shutil

from backend.config import settings

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(autouse = True)
def db_session(tmp_path):
    test_engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}", connect_args = {"check_same_thread": False})
    SQLModel.metadata.create_all(test_engine)

    def _db_get():
        with Session(test_engine) as session:
            yield session
    
    app.dependency_overrides[db_get] = _db_get
    
    with Session(test_engine) as session:
        yield session

    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(test_engine)
    test_engine.dispose()

@pytest.fixture(autouse = True)
def file_storage(tmp_path):
    tmp_storage_path = tmp_path / "userfiles"
    tmp_storage_path.mkdir()
    settings.FILE_STORAGE = tmp_storage_path
    yield settings.FILE_STORAGE

@pytest.fixture
def generate_csv(tmp_path):
    def _generate_csv(name: str = "test_file.csv", cols: int = 3, rows: int = 2) -> Path:
        headers = ",".join((f"col-{c}" for c in range(cols)))
        csv_rows = [headers]
        for r in range(rows):
            row = ",".join((f"val-{r}-{c}" for c in range(cols)))
            csv_rows.append(row)

        csv_text = "\n".join(csv_rows)
        csv_path = tmp_path / "input" / name
        csv_path.parent.mkdir(exist_ok = True)
        csv_path.write_text(csv_text)

        return csv_path
    return _generate_csv

