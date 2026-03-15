import pytest
from fastapi.testclient import TestClient
from backend.main import app
from pathlib import Path

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def generate_csv(tmp_path):
    def _generate_csv(name: str = "test_file.csv", cols: int = 3, rows: int = 2) -> Path:
        headers = ",".join((f"col-{c}" for c in range(cols)))
        csv_rows = [headers]
        for r in range(rows):
            row = ",".join((f"val-{r}-{c}" for c in range(cols)))
            csv_rows.append(row)

        csv_text = "\n".join(csv_rows)
        csv_path = tmp_path / name
        csv_path.write_text(csv_text)

        return csv_path
    return _generate_csv

