from backend.files.loaders.base import FileLoader
from backend.files.loaders.csv import CsvFileLoader
from backend.exceptions import (
    UnprocessableContentException,
    UnsupportedMediaTypeException,
)
from fastapi import UploadFile

_LOADERS: dict[str, type[FileLoader]] = {"text/csv": CsvFileLoader}


def get_file_loader(file: UploadFile) -> FileLoader:
    if file.content_type is None:
        raise UnprocessableContentException("Content-type is missing")

    loader = _LOADERS.get(file.content_type)

    if loader is None:
        raise UnsupportedMediaTypeException("Unsupported file type")

    return loader(file)
