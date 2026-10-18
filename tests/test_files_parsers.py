import pytest
from polars import LazyFrame, Schema, String

from backend.files.parsers import ColumnMapping, infer_mapping
from backend.files.parsers.mapping import (
    infer_mapping_id,
    infer_mapping_date,
    infer_mapping_value,
)


def test_infer_mapping__ok():
    test_data = {"ID": [1, 2], "DATE": ["2026-07-01", "2026-07-02"], "VALUE": [1, 2]}
    lf = LazyFrame(test_data)

    result = infer_mapping(lf)

    assert result == ColumnMapping(id="ID", date="DATE", value="VALUE", valid=True)


def test_infer_mapping__missing_id():
    test_data = {
        "INVALID_COL": [1, 2],
        "DATE": ["2026-07-01", "2026-07-02"],
        "VALUE": [1, 2],
    }
    lf = LazyFrame(test_data)

    result = infer_mapping(lf)

    assert result == ColumnMapping(id=None, date="DATE", value="VALUE", valid=False)


def test_infer_mapping__missing_date():
    test_data = {
        "ID": [1, 2],
        "INVALID_COL": ["2026-07-01", "2026-07-02"],
        "VALUE": [1, 2],
    }
    lf = LazyFrame(test_data)

    result = infer_mapping(lf)

    assert result == ColumnMapping(id="ID", date=None, value="VALUE", valid=False)


def test_infer_mapping__missing_value():
    test_data = {
        "ID": [1, 2],
        "DATE": ["2026-07-01", "2026-07-02"],
        "INVALID_COL": [1, 2],
    }
    lf = LazyFrame(test_data)

    result = infer_mapping(lf)

    assert result == ColumnMapping(id="ID", date="DATE", value=None, valid=False)


def test_infer_mapping__missing_all():
    test_data = {
        "INVALID_COL": [1, 2],
        "NOT_VALID_COL": ["2026-07-01", "2026-07-02"],
        "UNKNOWN_COL": [1, 2],
    }
    lf = LazyFrame(test_data)

    result = infer_mapping(lf)

    assert result == ColumnMapping(id=None, date=None, value=None, valid=False)


@pytest.mark.parametrize(
    "x", ("ID", "identifier", "KeY", "uid", "UUID", "EntRY", "RecoRd", "item", "NAME")
)
def test_infer_mapping_id__ok(x):
    schema = Schema({f"{x}": String, "dummy1": String, "dummy2": String})

    result = infer_mapping_id(schema)

    assert result == x


@pytest.mark.parametrize("x", ("Not working", "INVALID"))
def test_infer_mapping_id__missing(x):
    schema = Schema({f"{x}": String, "dummy1": String, "dummy2": String})

    result = infer_mapping_id(schema)

    assert result is None


@pytest.mark.parametrize("x", ("date", "Timestamp", "DateTime", "TIME", "DT"))
def test_infer_mapping_date__ok(x):
    schema = Schema({f"{x}": String, "dummy1": String, "dummy2": String})

    result = infer_mapping_date(schema)

    assert result == x


@pytest.mark.parametrize("x", ("Not working", "INVALID"))
def test_infer_mapping_date__missing(x):
    schema = Schema({f"{x}": String, "dummy1": String, "dummy2": String})

    result = infer_mapping_date(schema)

    assert result is None


@pytest.mark.parametrize(
    "x", ("value", "VAL", "amount", "AMT", "measurement", "sCoRe", "Result")
)
def test_infer_mapping_value__ok(x):
    schema = Schema({f"{x}": String, "dummy1": String, "dummy2": String})

    result = infer_mapping_value(schema)

    assert result == x


@pytest.mark.parametrize("x", ("Not working", "INVALID"))
def test_infer_mapping_value__missing(x):
    schema = Schema({f"{x}": String, "dummy1": String, "dummy2": String})

    result = infer_mapping_value(schema)

    assert result is None
