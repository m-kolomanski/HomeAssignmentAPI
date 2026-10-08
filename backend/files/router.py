from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select, col, func
from sqlalchemy.exc import IntegrityError
import polars as pl
from datetime import datetime
from io import BytesIO
import logging

from backend.database import db_get
from backend.files.loaders import FileLoader, get_file_loader
from backend.files.storage import FileStorage, get_file_storage
from backend.files.models import File
from backend.files.schemas import FileMetadataResponse

from backend.tags.models import Tag
from backend.file_tags.models import FileTag

logger = logging.getLogger(__name__)
router = APIRouter(tags=["files"])


@router.get("/files")
async def get_files(
    db: Session = Depends(db_get),
    name: str | None = None,
    tags: list[str] | None = Query(None),
):
    db_query = (
        select(File, Tag.name)
        .join(FileTag, FileTag.file_id == File.id, isouter=True)  # type: ignore[arg-type]
        .join(Tag, Tag.id == FileTag.tag_id, isouter=True)  # type: ignore[arg-type]
    )

    if name is not None:
        db_query = db_query.where(col(File.filename).icontains(name, autoescape=True))

    if tags is not None:
        searched_tags = set(tags)
        matching_ids = (
            select(FileTag.file_id)
            .join(Tag, col(Tag.id) == col(FileTag.tag_id))
            .where(col(Tag.name).in_(searched_tags))
            .group_by(col(FileTag.file_id))
            .having(func.count(func.distinct(col(Tag.id))) == len(searched_tags))
        )
        db_query = db_query.where(col(File.id).in_(matching_ids))

    files_with_tags = db.exec(db_query).all()

    result: dict[int, FileMetadataResponse] = {}

    for file, tag_name in files_with_tags:
        if file.id not in result:
            result[file.id] = FileMetadataResponse(**file.model_dump(), tags=[])
        if tag_name:
            result[file.id].tags.append(tag_name)

    return list(result.values())


@router.get("/files/{file_id}")
async def get_file(
    file_id: int,
    storage: FileStorage = Depends(get_file_storage),
):
    try:
        lf = storage.read(file_id)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File with ID {file_id} not found",
        )

    buf = BytesIO()
    lf.sink_csv(buf)
    buf.seek(0)

    return StreamingResponse(buf, media_type="text/csv")


@router.post("/files")
async def upload_files(
    db: Session = Depends(db_get),
    loader: FileLoader = Depends(get_file_loader),
    storage: FileStorage = Depends(get_file_storage),
):
    lf = loader.load()

    file_entry = File(
        filename=loader.basename,
        content_type=loader.content_type,
        size=loader.size,
        ncol=len(lf.collect_schema().names()),
        nrow=lf.select(pl.len()).collect().item(),
    )

    logger.info("Adding file: %s", file_entry.filename)

    try:
        db.add(file_entry)
        db.commit()
        db.refresh(file_entry)
    except IntegrityError:
        db.rollback()

        logger.critical("Unexpected error during file processing:", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error during file processing",
        )

    storage.write(file_entry.id, lf)

    return file_entry


@router.put("/files/{file_id}")
async def update_file(
    file_id: int,
    db: Session = Depends(db_get),
    loader: FileLoader = Depends(get_file_loader),
    storage: FileStorage = Depends(get_file_storage),
):
    file_entry = db.exec(select(File).where(File.id == file_id)).one_or_none()
    if not file_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    lf = loader.load()

    try:
        storage.write(file_entry.id, lf, overwrite=True)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File with ID {file_id} not found.",
        )

    file_entry.content_type = loader.content_type
    file_entry.size = loader.size
    file_entry.ncol = len(lf.collect_schema().names())
    file_entry.nrow = lf.select(pl.len()).collect().item()
    file_entry.updated_at = datetime.now()

    logger.info("Updating file: %s", file_entry.filename)

    db.add(file_entry)
    db.commit()
    db.refresh(file_entry)

    return file_entry
