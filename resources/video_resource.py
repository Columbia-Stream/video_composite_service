from fastapi import APIRouter, Query
from services.video_service import search_videos

router = APIRouter()

@router.get("/videos")
def list_videos(
    q: str = Query(None),
    course_id: str = Query(None),
    prof: str = Query(None),
    limit: int = 20,
    offset: int = 0,
):
    return search_videos(q, course_id, prof, limit, offset)