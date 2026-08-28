from fastapi import APIRouter, UploadFile, HTTPException, status, Depends
from fastapi.responses import FileResponse
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
import polars as pl
from datetime import datetime
from pathlib import Path
import logging

from backend.database import db_get
from backend.files.models import File
from backend.files.schemas import FileMetadataResponse

from backend.tags.models import Tag
from backend.file_tags.models import FileTag

from backend.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["files"])


@router.get("/files")
async def get_files(db: Session = Depends(db_get)):
    files_with_tags = db.exec(
        select(File, Tag.name)
        .join(FileTag, FileTag.file_id == File.id, isouter=True)  # type: ignore[arg-type]
        .join(Tag, Tag.id == FileTag.tag_id, isouter=True)  # type: ignore[arg-type]
    ).all()

    result: dict[int, FileMetadataResponse] = {}

    for file, tag_name in files_with_tags:
        if file.id not in result:
            result[file.id] = FileMetadataResponse(**file.model_dump(), tags=[])
        if tag_name:
            result[file.id].tags.append(tag_name)

    return list(result.values())


@router.get("/files/{filename}")
async def get_file(filename: str, db: Session = Depends(db_get)):
    file_basename = Path(filename).stem
    file_entry = db.exec(
        select(File).where(File.filename == file_basename)
    ).one_or_none()
    if not file_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    file_path = settings.FILE_STORAGE / f"{file_entry.id}.csv"

    return FileResponse(file_path)


@router.post("/files")
async def upload_files(file: UploadFile, db: Session = Depends(db_get)):
    if file.content_type != "text/csv":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Invalid file type",
        )

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Filename is required",
        )

    lf = pl.scan_csv(file.file)

    file_basename = Path(file.filename).stem

    file_entry = File(
        filename=file_basename,
        content_type=file.content_type,
        size=file.size,
        ncol=len(lf.collect_schema().names()),
        nrow=lf.select(pl.len()).collect().item(),
    )

    logger.info("Adding file: %s", file_entry.filename)

    try:
        db.add(file_entry)
        db.commit()
        db.refresh(file_entry)
    except IntegrityError as err:
        db.rollback()

        if "UNIQUE constraint failed" in str(err.orig):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="File already exists"
            )

        logger.critical("Unexpected error during file processing:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error during file processing",
        )

    file_path = settings.FILE_STORAGE / f"{file_entry.id}.csv"

    if file_path.exists():
        logger.critical(f"File path {file_path} already exists in storage.")
        raise HTTPException(
            status_code=500, detail="Unexpected error during file processing"
        )

    lf.sink_csv(file_path)

    return file_entry


@router.put("/files/{filename}")
async def update_file(filename: str, file: UploadFile, db: Session = Depends(db_get)):
    file_basename = Path(filename).stem
    file_entry = db.exec(
        select(File).where(File.filename == file_basename)
    ).one_or_none()
    if not file_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if not file.content_type:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Missing content type",
        )

    if not file.size:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Missing file size",
        )

    file_path = settings.FILE_STORAGE / f"{file_entry.id}.csv"

    lf = pl.scan_csv(file.file)
    lf.sink_csv(file_path)

    file_entry.content_type = file.content_type
    file_entry.size = file.size
    file_entry.ncol = len(lf.collect_schema().names())
    file_entry.nrow = lf.select(pl.len()).collect().item()
    file_entry.updated_at = datetime.now()

    logger.info("Updating file: %s", filename)

    db.add(file_entry)
    db.commit()
    db.refresh(file_entry)

    return file_entry
