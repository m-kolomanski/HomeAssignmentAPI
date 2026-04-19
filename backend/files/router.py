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

    if not file.filename:
        raise HTTPException(status_code = status.HTTP_422_UNPROCESSABLE_ENTITY, detail = "Filename is required")

    file_path = settings.FILE_STORAGE / file.filename

    if file_path.exists():
        raise HTTPException(status_code = 409, detail = "File already exists")
    
    lf = pl.scan_csv(file.file)
    lf.sink_csv(file_path)

    file_entry = File(
        filename = file.filename,
        content_type = file.content_type,
        size = file.size,
        ncol = len(lf.collect_schema().names()),
        nrow = lf.select(pl.len()).collect().item()
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
    
    if not file.content_type:
        raise HTTPException(status_code = status.HTTP_422_UNPROCESSABLE_ENTITY, detail = "Missing content type")
    
    if not file.size:
        raise HTTPException(status_code = status.HTTP_422_UNPROCESSABLE_CONTENT, detail = "Missing file size")

    file_path = settings.FILE_STORAGE / filename
    
    lf = pl.scan_csv(file.file)
    lf.sink_csv(file_path)
    
    file_entry.content_type = file.content_type
    file_entry.size = file.size
    file_entry.ncol = len(lf.collect_schema().names())
    file_entry.nrow = lf.select(pl.len()).collect().item()

    db.add(file_entry)
    db.commit()
    db.refresh(file_entry)

    return file_entry