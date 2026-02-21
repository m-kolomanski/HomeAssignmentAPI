from fastapi import APIRouter, File, UploadFile
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
