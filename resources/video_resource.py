from fastapi import APIRouter, Query, Body, HTTPException
from services.video_service import (
    search_videos,
    add_videodata,
    get_video_by_id,   # NEW IMPORT
)

router = APIRouter()


# --------------------------------------------------------
# 1. SEARCH VIDEOS
# --------------------------------------------------------
@router.get("/videos")
def list_videos(
    q: str = Query(None),
    course_id: str = Query(None),
    prof: str = Query(None),
    limit: int = 20,
    offset: int = 0,
):
    """
    Returns list of videos (search + filters).
    """
    return search_videos(q, course_id, prof, limit, offset)


# --------------------------------------------------------
# 2. ADD VIDEO METADATA (FROM UPLOAD SERVICE)
# --------------------------------------------------------
@router.post("/videos/metadata")
def store_video_metadata(
    video_id: str = Body(...),
    offering_id: int = Body(...),
    prof_uni: str = Body(...),
    title: str = Body(...),
    gcs_path: str = Body(...),
):
    """
    Receives video metadata from upload service.
    Stores in Videos table.
    """
    try:
        return add_videodata(
            video_id=video_id,
            offering_id=offering_id,
            prof_uni=prof_uni,
            title=title,
            gcs_path=gcs_path,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/videos/{video_id}")
def fetch_single_video(video_id: str):
    """
    Returns metadata for a single video by ID.
    Composite service calls this endpoint.
    """
    return get_video_by_id(video_id)
