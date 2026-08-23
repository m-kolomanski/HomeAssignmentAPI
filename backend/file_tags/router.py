from fastapi import APIRouter, HTTPException, status, Depends, Response
from sqlmodel import Session, select
import logging

from backend.database import db_get
from backend.file_tags.models import FileTag
from backend.files.models import File
from backend.tags.models import Tag

logger = logging.getLogger(__name__)
router = APIRouter(tags=["files"])


@router.post("/file/{filename}/tag")
async def tag_file(filename: str, tag_name: str, db: Session = Depends(db_get)):
    file_entry = db.exec(select(File).where(File.filename == filename)).one_or_none()


    if file_entry is None:
        logger.error("File not found: %s", filename)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"File '{filename}' not found"
        )

    tag_entry = db.exec(select(Tag).where(Tag.name == tag_name)).one_or_none()

    if tag_entry is None:
        logger.error("Tag not found: %s", tag_name)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Tag '{tag_name}' not found"
        )

    file_already_tagged = db.exec(
        select(FileTag).where(
            FileTag.file_id == file_entry.id, FileTag.tag_id == tag_entry.id
        )
    ).one_or_none()

    if file_already_tagged:
        logger.error("File: %s already tagged with: %s", filename, tag_name)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"File '{filename}' already has '{tag_name}' tag",
        )

    file_tag_entry = FileTag(file_id=file_entry.id, tag_id=tag_entry.id)

    logger.info("Adding new tag: %s to file: %s", tag_name, filename)

    db.add(file_tag_entry)
    db.commit()
    db.refresh(file_tag_entry)

    return file_tag_entry


@router.delete("/file/{filename}/tag")
async def untag_file(filename: str, tag_name: str, db: Session = Depends(db_get)):
    file_entry = db.exec(select(File).where(File.filename == filename)).one_or_none()

    if file_entry is None:
        logger.error("File not found: %s", filename)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"File '{filename}' not found"
        )

    tag_entry = db.exec(select(Tag).where(Tag.name == tag_name)).one_or_none()

    if tag_entry is None:
        logger.error("Tag not found: %s", tag_name)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Tag '{tag_name}' not found"
        )

    file_tag_entry = db.exec(
        select(FileTag).where(
            FileTag.file_id == file_entry.id, FileTag.tag_id == tag_entry.id
        )
    ).one_or_none()

    if not file_tag_entry:
        logger.error("File: %s does not have tag: %s", filename, tag_name)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"File '{filename}' dos not have '{tag_name}' tag",
        )

    logger.info("Deleting tag: %s from file: %s", tag_name, filename)

    db.delete(file_tag_entry)
    db.commit()

    return Response(status_code=status.HTTP_200_OK)
