import pytest
from polars import LazyFrame

from backend.files.storage.csv import CsvFileStorage
from backend.files.storage.parquet import ParquetFileStorage


@pytest.mark.parametrize("storage_class", [CsvFileStorage, ParquetFileStorage])
def test_files_storage_roundtrip(tmp_path, storage_class):
    storage = storage_class(tmp_path)
    test_data = {"a": [1, 2], "b": ["x", "y"]}
    lf = LazyFrame(test_data)

    storage.write(1, lf)
    result = storage.read(1).collect()

    assert result.to_dict(as_series=False) == test_data
