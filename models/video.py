from pydantic import BaseModel
from typing import Optional


class Video(BaseModel):
    video_id: str
    title: str
    gcs_path: str
    uploaded_at: str
    course_id: str
    course_name: str
    prof_uni: str

    # Optional if you want to return offering metadata
    semester: Optional[str] = None
    year: Optional[int] = None
    section: Optional[int] = None


class VideoMetadataInput(BaseModel):
    # This must match the string type you are using for the UUID
    video_id: str 
    # These fields are required and match the database types
    offering_id: int
    prof_uni: str
    title: str
    gcs_path: str
    # Note: We use Optional here if you expect some fields to be missing 
    # but based on your previous schema, most fields are NOT NULL.
