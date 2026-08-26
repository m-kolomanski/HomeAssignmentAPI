from fastapi import APIRouter, Response
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["system"])


@router.get("/health")
async def health():
    logger.info("API health check")
    return Response(status_code=200)
