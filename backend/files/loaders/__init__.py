from backend.files.loaders.base import FileLoader
from backend.files.loaders.csv import CsvFileLoader
from fastapi import UploadFile, HTTPException, status

__all__ = ["FileLoader", "CsvFileLoader", "get_file_loader"]

_LOADERS: dict[str, type[FileLoader]] = {"text/csv": CsvFileLoader}


def get_file_loader(file: UploadFile) -> FileLoader:
    if file.content_type is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Content-type is missing",
        )

    loader = _LOADERS.get(file.content_type)

    if loader is None:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type",
        )

    return loader(file)
