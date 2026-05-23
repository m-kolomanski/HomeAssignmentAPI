from fastapi import APIRouter, HTTPException, status, Depends, Response
from sqlmodel import Session, select

from ..database import db_get
from .models import FileTag
from ..files.models import File
from ..tags.models import Tag

router = APIRouter(tags=["files"])


@router.post("file/{filename}/tag")
async def tag_file(filename: str, tag_name: str, db: Session = Depends(db_get)):
    file_entry = db.exec(select(File).where(File.filename == filename)).one_or_none()

    if not file_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"File '{filename}' not found"
        )

    tag_entry = db.exec(select(Tag).where(Tag.name == tag_name)).one_or_none()

    if not tag_entry:
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
            detail=f"File '{filename}' already has '{tag_name}' tag",
        )

    file_tag_entry = FileTag(file_id=file_entry.id, tag_id=tag_entry.id)

    db.add(file_tag_entry)
    db.commit()
    db.refresh(file_tag_entry)

    return file_tag_entry


@router.post("file/{filename}/tag")
async def untag_file(filename: str, tag_name: str, db: Session = Depends(db_get)):
    file_entry = db.exec(select(File).where(File.filename == filename)).one_or_none()

    if not file_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"File '{filename}' not found"
        )

    tag_entry = db.exec(select(Tag).where(Tag.name == tag_name)).one_or_none()

    if not tag_entry:
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
            detail=f"File '{filename}' dos not have '{tag_name}' tag",
        )

    db.delete(file_tag_entry)
    db.commit()

    return Response(status_code=status.HTTP_200_OK)
