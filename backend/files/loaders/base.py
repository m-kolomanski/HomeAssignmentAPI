from abc import ABC, abstractmethod
from fastapi import HTTPException, UploadFile, status
from pathlib import Path
import polars as pl


class FileLoader(ABC):
    filename: str
    basename: str
    content_type: str
    size: int
    upload_file: UploadFile

    def __init__(self, upload_file: UploadFile):
        if upload_file.filename is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="File name is missing",
            )

        if upload_file.content_type is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Content-type is missing",
            )

        if upload_file.size is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="File size is missing",
            )

        self.filename = upload_file.filename
        self.basename = Path(upload_file.filename).stem
        self.content_type = upload_file.content_type
        self.size = upload_file.size
        self.upload_file = upload_file

    @abstractmethod
    def load(self) -> pl.LazyFrame: ...
