from fastapi import APIRouter, Query, Body, HTTPException, status
from services.video_service import (
    search_videos,
    add_videodata,
    get_video_by_id,
    get_instructors_by_offering,
    add_association,
    get_offerings
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
    year: int = Query(None),         # NEW
    semester: str = Query(None),     # NEW
    limit: int = 20,
    offset: int = 0,
):
    return search_videos(q, course_id, prof, year, semester, limit, offset)


# --------------------------------------------------------
# 2. ADD VIDEO METADATA
# --------------------------------------------------------
@router.post("/videos/metadata")
def store_video_metadata(
    video_id: str = Body(...),
    offering_id: int = Body(...),
    prof_uni: str = Body(...),
    title: str = Body(...),
    gcs_path: str = Body(...),
):
    try:
        existing_instructors = get_instructors_by_offering(offering_id)
        associated_unis = {inst['prof_uni'] for inst in existing_instructors}

        if existing_instructors:
            if prof_uni not in associated_unis:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Offering {offering_id} already taught by {', '.join(associated_unis)}."
                )
        else:
            add_association(offering_id=offering_id, prof_uni=prof_uni)

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
    return get_video_by_id(video_id)


@router.post("/videos/offer")
def list_offerings():
    return get_offerings()
