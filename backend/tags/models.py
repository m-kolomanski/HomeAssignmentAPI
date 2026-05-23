from sqlmodel import SQLModel, Field
from datetime import datetime


class Tag(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now())
