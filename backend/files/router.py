from fastapi import APIRouter, UploadFile, HTTPException, status
from fastapi.responses import FileResponse

from ..config import settings

router = APIRouter(tags = ["files"])

@router.get("/files")
async def get_files():
    return [f.name for f in settings.FILE_STORAGE.iterdir()]

@router.get("/files/{filename}")
async def get_file(filename: str):
    file_path = settings.FILE_STORAGE / filename

    if not file_path.exists():
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND)

    return FileResponse(file_path)

@router.post("/files")
async def upload_files(file: UploadFile):
    if file.content_type != "text/csv":
        raise HTTPException(status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail = "Invalid file type")
    
    file_path = settings.FILE_STORAGE / file.filename

    if file_path.exists():
        raise HTTPException(status_code = 409, detail = "File already exists")

    contents = await file.read()

    with file_path.open("wb") as f:
        f.write(contents)

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(contents)
    }

@router.put("/files/{filename}")
async def update_file(filename: str, file: UploadFile):
    file_path = settings.FILE_STORAGE / filename

    if not file_path.exists():
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND)
    
    contents = await file.read()

    with file_path.open("wb") as f:
        f.write(contents)

    return {
        "filename": filename,
        "content_type": file.content_type,
        "size": len(contents)
    }