from utils.db import get_db_connection
from fastapi import HTTPException


# -----------------------------------------------------------
# SEARCH WITH year + semester
# -----------------------------------------------------------
def search_videos(q=None, course_id=None, prof=None, year=None, semester=None, limit=20, offset=0):
    """
    Search videos using JOINs:
    - Videos
    - CourseOfferings (with year + semester)
    - Courses
    - CourseInstructors
    """

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                v.video_id,
                v.title,
                v.gcs_path,
                v.uploaded_at,
                co.course_id,
                co.year,
                co.semester,
                c.course_name,
                v.prof_uni
            FROM Videos v
            JOIN CourseOfferings co ON v.offering_id = co.offering_id
            JOIN Courses c ON co.course_id = c.course_id
            JOIN CourseInstructors ci 
                ON ci.offering_id = co.offering_id
                AND ci.prof_uni = v.prof_uni
            WHERE 1=1
        """

        params = []

        # Keyword search
        if q:
            query += " AND v.title LIKE %s"
            params.append(f"%{q}%")

        # Course ID filter
        if course_id:
            query += " AND co.course_id = %s"
            params.append(course_id)

        # Professor UNI filter
        if prof:
            query += " AND ci.prof_uni = %s"
            params.append(prof)

        # NEW: Year filter
        if year:
            query += " AND co.year = %s"
            params.append(year)

        # NEW: Semester filter
        if semester:
            query += " AND co.semester = %s"
            params.append(semester)

        # Ordering + pagination
        query += " ORDER BY v.uploaded_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        # Add HATEOAS links
        for item in rows:
            item["links"] = [
                {"rel": "self", "href": f"/videos/{item['video_id']}"},
                {"rel": "course", "href": f"/courses/{item['course_id']}"}
            ]

        return {
            "items": rows,
            "page_size": limit,
            "offset": offset,
            "links": [
                {"rel": "self", "href": f"/videos?limit={limit}&offset={offset}"}
            ],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")



# -----------------------------------------------------------
# Insert video metadata (REQUIRED)
# -----------------------------------------------------------
def add_videodata(video_id: str = None, offering_id: int = None,
                  prof_uni: str = None, title: str = None, gcs_path: str = None):
    """
    Add video metadata into Videos table.
    """

    insert_query = """
        INSERT INTO Videos (video_id, offering_id, prof_uni, title, gcs_path)
        VALUES (%s, %s, %s, %s, %s)
    """

    data_tuple = (video_id, offering_id, prof_uni, title, gcs_path)

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(insert_query, data_tuple)
        conn.commit()

        cursor.close()
        conn.close()

        return {"message": "Video metadata added successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")



# -----------------------------------------------------------
# Get instructors by offering_id (REQUIRED)
# -----------------------------------------------------------
def get_instructors_by_offering(offering_id: int):
    query = """
        SELECT * FROM CourseInstructors 
        WHERE offering_id = %s
    """

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (offering_id,))
            return cursor.fetchall()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error retrieving instructors: {str(e)}")



# -----------------------------------------------------------
# Add new offering_id → prof association (REQUIRED)
# -----------------------------------------------------------
def add_association(offering_id: int = None, prof_uni: str = None):

    insert_query = """
        INSERT INTO CourseInstructors (offering_id, prof_uni)
        VALUES (%s, %s)
    """

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(insert_query, (offering_id, prof_uni))
        conn.commit()

        cursor.close()
        conn.close()

        return {"message": "Professor added to offering successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")



# -----------------------------------------------------------
# Fetch a single video (REQUIRED)
# -----------------------------------------------------------
def get_video_by_id(video_id: str):

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                v.video_id,
                v.title,
                v.gcs_path,
                v.uploaded_at,
                co.course_id,
                c.course_name,
                v.prof_uni
            FROM Videos v
            LEFT JOIN CourseOfferings co ON v.offering_id = co.offering_id
            LEFT JOIN Courses c ON co.course_id = c.course_id
            WHERE v.video_id = %s
        """

        cursor.execute(query, (video_id,))
        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Video not found")

        row["links"] = [
            {"rel": "self", "href": f"/videos/{video_id}"},
            {"rel": "course", "href": f"/courses/{row['course_id']}"} if row["course_id"] else {}
        ]

        return row

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")



# -----------------------------------------------------------
# Fetch all offerings (REQUIRED)
# -----------------------------------------------------------
def get_offerings():

    query = """
        SELECT * FROM CourseOfferings
    """

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query)
            return cursor.fetchall()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error retrieving offerings: {str(e)}")
