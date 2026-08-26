from sqlmodel import SQLModel, Field


class FileTag(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    file_id: int = Field(foreign_key="file.id")
    tag_id: int = Field(foreign_key="tag.id")
