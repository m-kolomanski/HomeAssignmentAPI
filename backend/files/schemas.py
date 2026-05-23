from pydantic import BaseModel
from datetime import datetime


class FileMetadataResponse(BaseModel):
    id: int
    filename: str
    tags: list[str] = []
    content_type: str
    size: int
    ncol: int
    nrow: int
    uploaded_at: datetime
    updated_at: datetime
