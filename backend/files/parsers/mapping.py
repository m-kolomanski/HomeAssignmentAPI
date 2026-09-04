from polars import LazyFrame, Schema
from dataclasses import dataclass

_ID_NAME_HINTS = (
    "id",
    "identifier",
    "key",
    "uid",
    "uuid",
    "entry",
    "record",
    "item",
    "name",
)
_DATE_NAME_HINTS = ("date", "timestamp", "datetime", "time", "dt")
_VALUE_NAME_HINTS = ("value", "val", "amount", "amt", "measurement", "score", "result")


@dataclass
class ColumnMapping:
    id: str | None
    date: str | None
    value: str | None
    valid: bool


def infer_mapping(lf: LazyFrame) -> ColumnMapping:
    schema = lf.collect_schema()
    mapping_id = infer_mapping_id(schema)
    mapping_date = infer_mapping_date(schema)
    mapping_value = infer_mapping_value(schema)
    is_valid = not any((m is None for m in (mapping_id, mapping_date, mapping_value)))

    return ColumnMapping(
        id=mapping_id, date=mapping_date, value=mapping_value, valid=is_valid
    )


def infer_mapping_id(schema: Schema) -> str | None:
    for name in schema.names():
        if name.strip().lower() in _ID_NAME_HINTS:
            return name

    return None


def infer_mapping_date(schema: Schema) -> str | None:
    for name in schema.names():
        if name.strip().lower() in _DATE_NAME_HINTS:
            return name
    return None


def infer_mapping_value(schema: Schema) -> str | None:
    for name in schema.names():
        if name.strip().lower() in _VALUE_NAME_HINTS:
            return name
    return None
