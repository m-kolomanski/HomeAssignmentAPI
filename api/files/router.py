from fastapi import APIRouter, UploadFile, Response
from fastapi.responses import FileResponse
import os

router = APIRouter(tags = ["files"])

@router.post("/files")
async def upload_files(file: UploadFile):
    contents = await file.read()

    with open(f"/app/userfiles/{file.filename}", "wb") as f:
        f.write(contents)

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(contents)
    }

@router.get("/files")
async def get_files():
    return os.listdir("/app/userfiles")

@router.get("/files/{filename}")
async def get_file(filename: str):
    return FileResponse(f"/app/userfiles/{filename}")
