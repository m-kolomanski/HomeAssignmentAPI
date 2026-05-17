from sqlmodel import SQLModel, Field
from datetime import datetime

class File(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    filename: str
    content_type: str
    size: int
    ncol: int
    nrow: int
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now())
