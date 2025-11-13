from fastapi import APIRouter, Query
from services.video_service import search_videos

router = APIRouter()

@router.get("/videos")
def list_videos(
    q: str = Query(None),
    offering_id: int = Query(None),
    prof: str = Query(None),
    limit: int = Query(20),
    offset: int = Query(0)
):
    """
    Public endpoint for Search/Upload microservices to query videos.
    No authentication required (internal only).
    """
    return search_videos(q, offering_id, prof, limit, offset)
