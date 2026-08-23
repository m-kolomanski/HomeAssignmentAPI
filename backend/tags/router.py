from fastapi import APIRouter, HTTPException, status, Depends, Response
from sqlmodel import Session, select, delete
import logging

from backend.database import db_get
from backend.tags.models import Tag

logger = logging.getLogger(__name__)
router = APIRouter(tags=["tags"])

@router.get("/tags")
async def get_tags(db: Session = Depends(db_get)):
    return db.exec(select(Tag)).all()


@router.post("/tags")
async def upload_tags(name: str, db: Session = Depends(db_get)):
    tag_exists = db.exec(select(Tag).where(Tag.name == name)).one_or_none()

    if tag_exists:
        logger.error("Tag already exists: %s", name)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    tag_entry = Tag(name=name)

    logger.info("Adding new tag: %s", name)
    db.add(tag_entry)
    db.commit()
    db.refresh(tag_entry)

    return tag_entry


@router.delete("/tags")
async def delete_tag(name: str, db: Session = Depends(db_get)):
    tag_exists = db.exec(select(Tag).where(Tag.name == name)).one_or_none()

    if not tag_exists:
        logger.error("Tag does not exist: %s", name)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    db.exec(delete(Tag).where(Tag.id == tag_exists.id))  # type: ignore[arg-type]
    db.commit()

    return Response(status_code=status.HTTP_200_OK)
