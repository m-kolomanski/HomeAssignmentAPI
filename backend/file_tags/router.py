from fastapi import APIRouter, HTTPException, status, Depends, Response
import logging
from sqlmodel import Session, col, select

from backend.database import db_get
from backend.file_tags.models import FileTag
from backend.files.models import File
from backend.tags.models import Tag

logger = logging.getLogger(__name__)
router = APIRouter(tags=["files"])


@router.get("/files/{file_id}/tags")
async def get_file_tags(file_id: int, db: Session = Depends(db_get)):
    file_entry = db.exec(select(File).where(File.id == file_id)).one_or_none()

    if file_entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File with ID '{file_id}' not found",
        )

    file_tags = db.exec(
        select(Tag.name)
        .join(FileTag, col(FileTag.tag_id) == col(Tag.id))
        .where(FileTag.file_id == file_entry.id)
    ).all()

    return file_tags


@router.post("/files/{file_id}/tags")
async def tag_file(file_id: int, tag_name: str, db: Session = Depends(db_get)):
    file_entry = db.exec(select(File).where(File.id == file_id)).one_or_none()

    if file_entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File with ID '{file_id}' not found",
        )

    tag_entry = db.exec(select(Tag).where(Tag.name == tag_name)).one_or_none()

    if tag_entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Tag '{tag_name}' not found"
        )

    file_already_tagged = db.exec(
        select(FileTag).where(
            FileTag.file_id == file_entry.id, FileTag.tag_id == tag_entry.id
        )
    ).one_or_none()

    if file_already_tagged:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"File '{file_id}' already has '{tag_name}' tag",
        )

    file_tag_entry = FileTag(file_id=file_entry.id, tag_id=tag_entry.id)

    logger.info("Adding new tag: %s to file: %s", tag_name, file_id)

    db.add(file_tag_entry)
    db.commit()
    db.refresh(file_tag_entry)

    return file_tag_entry


@router.delete("/files/{file_id}/tags")
async def untag_file(file_id: int, tag_name: str, db: Session = Depends(db_get)):
    file_entry = db.exec(select(File).where(File.id == file_id)).one_or_none()

    if file_entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File with ID '{file_id}' not found",
        )

    tag_entry = db.exec(select(Tag).where(Tag.name == tag_name)).one_or_none()

    if tag_entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Tag '{tag_name}' not found"
        )

    file_tag_entry = db.exec(
        select(FileTag).where(
            FileTag.file_id == file_entry.id, FileTag.tag_id == tag_entry.id
        )
    ).one_or_none()

    if not file_tag_entry:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"File '{file_id}' does not have '{tag_name}' tag",
        )

    logger.info("Deleting tag: %s from file: %s", tag_name, file_id)

    db.delete(file_tag_entry)
    db.commit()

    return Response(status_code=status.HTTP_200_OK)
