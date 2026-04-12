from fastapi import APIRouter, UploadFile, HTTPException, status, Depends
from fastapi.responses import FileResponse
from sqlmodel import Session, select
import polars as pl
from ..database import db_get
from .models import File

from ..config import settings

router = APIRouter(tags = ["files"])

@router.get("/files")
async def get_files(db: Session = Depends(db_get)):
    return db.exec(select(File)).all()

@router.get("/files/{filename}")
async def get_file(filename: str, db: Session = Depends(db_get)):
    file_entry = db.exec(select(File).where(File.filename == filename)).one_or_none()
    if not file_entry:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND)

    file_path = settings.FILE_STORAGE / filename

    return FileResponse(file_path)

@router.post("/files")
async def upload_files(file: UploadFile, db: Session = Depends(db_get)):
    if file.content_type != "text/csv":
        raise HTTPException(status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail = "Invalid file type")
    
    file_path = settings.FILE_STORAGE / file.filename

    if file_path.exists():
        raise HTTPException(status_code = 409, detail = "File already exists")

    contents = await file.read()

    with file_path.open("wb") as f:
        f.write(contents)
    
    p = pl.read_csv(file_path)
    
    shape = p.shape

    file_entry = File(
        filename = file.filename,
        content_type = file.content_type,
        size = len(contents),
        ncol = shape[1],
        nrow = shape[0]
    )
    
    db.add(file_entry)
    db.commit()
    db.refresh(file_entry)

    return file_entry

@router.put("/files/{filename}")
async def update_file(filename: str, file: UploadFile, db: Session = Depends(db_get)):
    file_entry = db.exec(select(File).where(File.filename == filename)).one_or_none()
    if not file_entry:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND)

    file_path = settings.FILE_STORAGE / filename
    
    contents = await file.read()

    with file_path.open("wb") as f:
        f.write(contents)

    p = pl.read_csv(file_path)
    shape = p.shape
    
    file_entry.content_type = file.content_type
    file_entry.size = len(contents)
    file_entry.ncol = shape[1]
    file_entry.nrow = shape[0]

    db.add(file_entry)
    db.commit()
    db.refresh(file_entry)

    return file_entry