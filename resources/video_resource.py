from fastapi import APIRouter, Query, Body, HTTPException
from services.video_service import search_videos, add_videodata

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


@router.post("/videos/metadata")
def store_video_metadata(
    # Use 'str' for the video_id, as it's a UUID string
    video_id: str = Body(...), 
    
    # 'int' is correct
    offering_id: int = Body(...), 
    
    # 'str' is correct
    prof_uni: str = Body(...), 
    
    # 'text' is not a valid Python type hint, use 'str'
    title: str = Body(...), 
    
    # This field *must* match the JSON key from the Upload service
    # which we defined as 'raw_gcs_path'
    gcs_path: str = Body(...) 
):
    """
    Receives metadata from the Upload service (via JSON body)
    and passes it to the database insertion function.
    """
    try:
        # Call the database function, mapping the incoming JSON key 
        # 'raw_gcs_path' to the function's 'gcs_path' argument.
        return add_videodata(
            video_id=video_id, 
            offering_id=offering_id, 
            prof_uni=prof_uni, 
            title=title, 
            gcs_path=gcs_path # <-- This mapping is critical
        )
    except Exception as e:
        # Catch errors from add_videodata
        raise HTTPException(status_code=500, detail=str(e))