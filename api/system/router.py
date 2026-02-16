from fastapi import APIRouter, Response

router = APIRouter(tags = ["system"])

@router.get("/health")
async def health():
    return Response(status_code = 200)
