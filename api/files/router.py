from fastapi import APIRouter, UploadFile, Response
from fastapi.responses import FileResponse
import os

FILE_STORAGE = "/app/userfiles"

router = APIRouter(tags = ["files"])

@router.get("/files")
async def get_files():
    return os.listdir(FILE_STORAGE)

@router.get("/files/{filename}")
async def get_file(filename: str):
    file_path = f"{FILE_STORAGE}/{filename}"

    if not os.path.exists(file_path):
        return Response(status_code = 404)

    return FileResponse(file_path)

@router.post("/files")
async def upload_files(file: UploadFile):
    contents = await file.read()

    with open(f"{FILE_STORAGE}/{file.filename}", "wb") as f:
        f.write(contents)

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(contents)
    }

@router.put("/files/{filename}")
async def update_file(filename: str, file: UploadFile):
    file_path = f"{FILE_STORAGE}/{filename}"

    if not os.path.exists(file_path):
        return Response(status_code = 404)
    
    contents = await file.read()

    with open(file_path, "wb") as f:
        f.write(contents)

    return {
        "filename": filename,
        "content_type": file.content_type,
        "size": len(contents)
    }